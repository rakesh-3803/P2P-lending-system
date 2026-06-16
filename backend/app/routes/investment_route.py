from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.investment_model import Investment
from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.notification_model import Notification
from app.models.emi_model import EMI

from app.utils.time_utils import get_ist_time
from app.utils.date_utils import add_months

from app.schemas.investment_schema import InvestmentCreate

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role

router = APIRouter()


@router.post("/invest")
def invest_in_loan(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    loan = db.query(Loan).filter(
        Loan.id == investment.loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="This loan is already funded or not available"
        )

    if investment.amount != loan.amount:
        raise HTTPException(
            status_code=400,
            detail=f"You must invest full loan amount ₹{loan.amount}"
        )

    existing_investment = db.query(Investment).filter(
        Investment.loan_id == loan.id
    ).first()

    if existing_investment:
        raise HTTPException(
            status_code=400,
            detail="Loan already funded"
        )

    lender_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not lender_wallet:
        raise HTTPException(
            status_code=404,
            detail="Lender wallet not found"
        )

    if lender_wallet.balance < investment.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == loan.borrower_id
    ).first()

    if not borrower_wallet:
        raise HTTPException(
            status_code=404,
            detail="Borrower wallet not found"
        )

    new_investment = Investment(
        lender_id=user["user_id"],
        loan_id=loan.id,
        amount=investment.amount
    )

    db.add(new_investment)

    lender_wallet.balance -= investment.amount
    borrower_wallet.balance += investment.amount

    loan.status = "FUNDED"

    # =========================================
    # GENERATE EMI SCHEDULE WITH DUE DATES
    # =========================================
    
    # Borrower pays original interest + 2% convenience fee
    borrower_interest_rate = loan.interest_rate + 2

    total_repayment = (
        loan.amount +
        (
            loan.amount * borrower_interest_rate / 100
        )
    )
    emi_amount = round(
        total_repayment / loan.tenure_months,
        2
    )

    funded_date = get_ist_time()

    for emi_number in range(
        1,
        loan.tenure_months + 1
    ):

        due_date = add_months(
            funded_date,
            emi_number
        )

        emi = EMI(
            loan_id=loan.id,
            borrower_id=loan.borrower_id,
            emi_number=emi_number,
            amount=emi_amount,
            due_date=due_date,
            status="PENDING"
        )

        db.add(emi)

    lender_transaction = Transaction(
        user_id=user["user_id"],
        amount=investment.amount,
        transaction_type="DEBIT",
        description="Loan investment"
    )

    borrower_transaction = Transaction(
        user_id=loan.borrower_id,
        amount=investment.amount,
        transaction_type="CREDIT",
        description="Loan amount received"
    )

    db.add(lender_transaction)
    db.add(borrower_transaction)

    first_due_date = add_months(
        funded_date,
        1
    )

    borrower_notification = Notification(
        user_id=loan.borrower_id,
        message=(
            f"₹{investment.amount} credited to your wallet. "
            f"{loan.tenure_months} EMI schedule generated. "
            f"Your first EMI of ₹{emi_amount} is due on "
            f"{first_due_date.strftime('%d-%m-%Y')}."
        )
    )

    lender_notification = Notification(
        user_id=user["user_id"],
        message=f"You invested ₹{investment.amount} successfully"
    )

    db.add(borrower_notification)
    db.add(lender_notification)

    db.commit()
    db.refresh(new_investment)

    return {
        "message": "Investment successful. Loan is now funded.",
        "investment_id": new_investment.id,
        "loan_status": loan.status,
        "remaining_balance": lender_wallet.balance,
        "emi_amount": emi_amount,
        "number_of_emis": loan.tenure_months,
        "first_emi_due_date": first_due_date
    }


@router.get("/my-investments")
def my_investments(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    investments = db.query(Investment).filter(
        Investment.lender_id == user["user_id"]
    ).all()

    result = []

    for investment in investments:

        loan = db.query(Loan).filter(
            Loan.id == investment.loan_id
        ).first()

        if loan:

            result.append({

                "investment_id": investment.id,

                "loan_id": loan.id,

                "borrower_id": loan.borrower_id,

                "amount_invested": investment.amount,

                "loan_amount": loan.amount,

                "interest_rate": loan.interest_rate,

                "purpose": loan.purpose,

                "status": loan.status,

                "expected_return":
                    investment.amount +
                    (
                        investment.amount *
                        loan.interest_rate / 100
                    )

            })

    return result
@router.get("/lender/portfolio-summary")
def lender_portfolio_summary(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    investments = db.query(Investment).filter(
        Investment.lender_id == user["user_id"]
    ).all()

    total_invested = 0
    total_expected_return = 0
    active_investments = 0
    completed_investments = 0

    recent_investments = []

    for investment in investments:

        loan = db.query(Loan).filter(
            Loan.id == investment.loan_id
        ).first()

        if loan:

            expected_return = (
                investment.amount +
                (
                    investment.amount *
                    loan.interest_rate / 100
                )
            )

            total_invested += investment.amount
            total_expected_return += expected_return

            if loan.status == "FUNDED":
                active_investments += 1

            if loan.status == "COMPLETED":
                completed_investments += 1

            recent_investments.append({
                "investment_id": investment.id,
                "loan_id": loan.id,
                "amount_invested": investment.amount,
                "expected_return": expected_return,
                "loan_status": loan.status,
                "purpose": loan.purpose,
                "created_at": investment.created_at
            })

    total_profit = total_expected_return - total_invested

    recent_investments = sorted(
        recent_investments,
        key=lambda item: item["created_at"],
        reverse=True
    )[:5]

    return {
        "total_invested": total_invested,
        "total_expected_return": total_expected_return,
        "total_profit": total_profit,
        "active_investments": active_investments,
        "completed_investments": completed_investments,
        "recent_investments": recent_investments
    }