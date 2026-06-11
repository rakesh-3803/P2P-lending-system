import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from groq import Groq

from app.database.db_dependency import get_db

from app.schemas.ai_agent_schema import AIQuestion

from app.auth.auth_bearer import verify_token

from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.notification_model import Notification
from app.models.investment_model import Investment
from app.models.emi_model import EMI
from app.models.bank_account_model import BankAccount
from app.models.borrower_profile_model import BorrowerProfile
from app.models.user_model import User

router = APIRouter()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


@router.post("/ai-agent/ask")
def ask_ai_agent(
    request: AIQuestion,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY not configured"
        )

    question = request.question
    role = user["role"].upper()
    user_id = user["user_id"]

    context = []

    # COMMON DATA
    wallet = db.query(Wallet).filter(
        Wallet.user_id == user_id
    ).first()

    context.append(
        f"Wallet balance: ₹{wallet.balance if wallet else 0}"
    )

    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).all()

    context.append(
        f"Notifications count: {len(notifications)}"
    )

    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).all()

    context.append(
        f"Transactions count: {len(transactions)}"
    )

    context.append(
        f"Transactions: {[{'id': t.id, 'amount': t.amount, 'type': t.transaction_type, 'description': t.description} for t in transactions]}"
    )

    context.append(
        f"Notifications: {[{'id': n.id, 'message': n.message, 'status': n.status} for n in notifications]}"
    )

    # BORROWER DATA
    if role == "BORROWER":

        loans = db.query(Loan).filter(
            Loan.borrower_id == user_id
        ).all()

        emis = db.query(EMI).filter(
            EMI.borrower_id == user_id
        ).all()

        pending_emis = [
            emi for emi in emis
            if emi.status == "PENDING"
        ]

        paid_emis = [
            emi for emi in emis
            if emi.status == "PAID"
        ]

        total_pending_amount = sum(
            emi.amount for emi in pending_emis
        )

        total_paid_amount = sum(
            emi.amount for emi in paid_emis
        )

        profile = db.query(BorrowerProfile).filter(
            BorrowerProfile.user_id == user_id
        ).first()

        bank = db.query(BankAccount).filter(
            BankAccount.user_id == user_id
        ).first()

        context.append(
            f"Borrower loans: {[{'id': l.id, 'amount': l.amount, 'interest_rate': l.interest_rate, 'tenure_months': l.tenure_months, 'purpose': l.purpose, 'status': l.status} for l in loans]}"
        )

        context.append(
            f"""
EMI Summary:
Total EMIs: {len(emis)}
Pending EMIs: {len(pending_emis)}
Paid EMIs: {len(paid_emis)}
Total pending EMI amount: ₹{total_pending_amount}
Total paid EMI amount: ₹{total_paid_amount}
EMI list: {[{'id': e.id, 'emi_number': e.emi_number, 'amount': e.amount, 'status': e.status} for e in emis]}

IMPORTANT:
Do not subtract loan principal from pending EMI amount.
The total pending EMI amount is the exact remaining amount the borrower must pay.
"""
        )

        context.append(
            f"Credit score: {profile.credit_score if profile else 'not available'}"
        )

        context.append(
            f"Borrower profile: {profile.__dict__ if profile else 'not available'}"
        )

        context.append(
            f"Bank account linked: {'yes' if bank else 'no'}"
        )

        if bank:
            context.append(
                f"Bank account details: bank={bank.bank_name}, holder={bank.account_holder}, bank_balance=₹{bank.balance}"
            )

    # LENDER DATA
    if role == "LENDER":

        investments = db.query(Investment).filter(
            Investment.lender_id == user_id
        ).all()

        investment_details = []

        total_expected_return = 0

        for investment in investments:

            loan = db.query(Loan).filter(
                Loan.id == investment.loan_id
            ).first()

            expected_return = investment.amount

            if loan:
                expected_return = (
                    investment.amount +
                    (
                        investment.amount *
                        loan.interest_rate / 100
                    )
                )

                total_expected_return += expected_return

                investment_details.append({
                    "investment_id": investment.id,
                    "loan_id": investment.loan_id,
                    "amount_invested": investment.amount,
                    "loan_amount": loan.amount,
                    "interest_rate": loan.interest_rate,
                    "purpose": loan.purpose,
                    "loan_status": loan.status,
                    "expected_return": expected_return
                })

        approved_loans = db.query(Loan).filter(
            Loan.status == "APPROVED"
        ).all()

        context.append(
            f"Investments: {investment_details}"
        )

        context.append(
            f"Total expected return: ₹{total_expected_return}"
        )

        context.append(
            f"Approved loans available: {[{'id': l.id, 'amount': l.amount, 'interest_rate': l.interest_rate, 'tenure_months': l.tenure_months, 'purpose': l.purpose} for l in approved_loans]}"
        )

    # ADMIN DATA
    if role == "ADMIN":

        total_users = db.query(User).count()
        total_loans = db.query(Loan).count()

        pending_loans = db.query(Loan).filter(
            Loan.status == "PENDING"
        ).count()

        approved_loans = db.query(Loan).filter(
            Loan.status == "APPROVED"
        ).count()

        funded_loans = db.query(Loan).filter(
            Loan.status == "FUNDED"
        ).count()

        completed_loans = db.query(Loan).filter(
            Loan.status == "COMPLETED"
        ).count()

        context.append(
            f"""
Admin Summary:
Total users: {total_users}
Total loans: {total_loans}
Pending loans: {pending_loans}
Approved loans: {approved_loans}
Funded loans: {funded_loans}
Completed loans: {completed_loans}
"""
        )

    system_prompt = """
You are FinFlow AI, a domain-specific assistant for a P2P lending system.

Rules:
1. Use only the backend-provided user data.
2. Do not invent or assume missing values.
3. Do not recalculate loan, EMI, wallet, repayment, or investment values unless the backend already provides them.
4. Do not subtract principal from EMI pending amount.
5. If total pending EMI amount is provided, report it exactly.
6. If data is not available, clearly say it is not available.
7. Keep answers short, clear, and practical.
8. Format answers with headings and bullet points.
9. Never expose raw internal tokens or backend implementation details.

Response format:
Start with a short direct answer.
Then show key details in bullet points.
Then give a final next action.
"""

    user_prompt = f"""
User role: {role}

Backend-provided user data:
{chr(10).join(context)}

User question:
{question}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.1
    )

    return {
        "answer": completion.choices[0].message.content
    }