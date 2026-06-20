x = float(input("What's x? "))
y = float(input("What's y? "))
# Here I combined two format spec in one to display a thousand separator and round to two decimal places
print(f"{x / y:,.2f}")