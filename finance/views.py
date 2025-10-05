from django.shortcuts import render, redirect ,HttpResponse
from finance.forms import RegisterForm , TransactionForm , GoalForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Transaction , Goal
from django.db.models import Sum
from .admin import TransactionResource

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request , user)
            return redirect("dashboard")  
        
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})



@login_required(login_url='login')
def dashboard_view(request):
    transactions = Transaction.objects.filter(user = request.user)
    goals = Goal.objects.filter(user = request.user)

    #calculate total income and expenses

    total_income = Transaction.objects.filter(user = request.user , transaction_type = "Income").aggregate(Sum("amount"))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(user = request.user , transaction_type = "Expense").aggregate(Sum("amount"))['amount__sum'] or 0
    net_savings = total_income - total_expense

    remaining_saving = net_savings

    goal_progress = []
    for goal in goals:
        if remaining_saving >= goal.target_amount:
            goal_progress.append({'goal' : goal , "progress" : 100})
            remaining_saving -= goal.target_amount
        elif remaining_saving > 0:
            progress = (remaining_saving/goal.target_amount) * 100
            goal_progress.append({"goal" : goal , "progress" : progress})
            remaining_saving = 0
        else:
            goal_progress.append({'goal' : goal , "progress" : 0})


    context = {
        'transactions' : transactions,
        'total_income' : total_income,
        'total_expense' : total_expense,
        'net_saving' : net_savings,
        'goal_progress' : goal_progress,
    }
    return render(request, "dashboard.html" , context)


@login_required
def transaction_view(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit= False)  
            transaction.user = request.user
            transaction.save()
            print(" Transaction saved:", transaction)
            return redirect("transaction_list")  
        else:
            print(" Form errors:", form.errors) 
    else:
        form = TransactionForm()   # GET ke liye form banana jaruri hai

    return render(request, "transaction_forms.html", {"form": form})



@login_required
def transactionlist_view(request):
    transactions = Transaction.objects.filter(user = request.user)
    return render(request, "transaction_list.html", {"transactions": transactions})




@login_required  
def goal_view(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('dashboard')
    else:
        form = GoalForm()

    # har case me return hona chahiye
    return render(request, 'goal_form.html', {'form': form})

def export_transactions(request):
    user_transactions = Transaction.objects.filter(user = request.user)

    transaction_resource = TransactionResource()
    dataset = transaction_resource.export(queryset= user_transactions)

    excel_data = dataset.export('xlsx')


    # Create an HttpResponse with the correct MIME type for an Excel file
    response = HttpResponse(
        excel_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Response with headers for file download
    response['Content-Disposition'] = 'attachment; filename="transactions_report.xlsx"'
    return response

