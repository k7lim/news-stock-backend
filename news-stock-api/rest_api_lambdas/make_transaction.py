import boto3

def lambda_handler(event, context):
    # Get the requested action from the event
    action = event.get("action", "")
    if action not in ["buy", "sell"]:
        raise ValueError("Invalid action provided")

    # Get user information and stock information from event
    user_id = event.get("user_id", "")
    symbol = event.get("symbol", "")
    shares = event.get("shares", 0)
    price = event.get("price", 0)

    # Connect to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("NewsStock_Portfolios")

    # Buy stocks
    if action == "buy":
        # Get user information from DynamoDB
        response = table.get_item(Key={"user_id": user_id})
        item = response.get("Item", {})
        current_balance = item.get("balance", 0)

        # Check if user has enough funds to buy the stock
        total_cost = shares * price
        if total_cost > current_balance:
            raise ValueError("Insufficient funds")

        # Deduct the cost from the user's balance and update the portfolio
        new_balance = current_balance - total_cost
        portfolio = item.get("portfolio", {})
        portfolio[symbol] = portfolio.get(symbol, 0) + shares
        table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set balance=:b, portfolio=:p",
            ExpressionAttributeValues={
                ":b": new_balance,
                ":p": portfolio
            }
        )

    # Sell stocks
    elif action == "sell":
        # Get user information from DynamoDB
        response = table.get_item(Key={"user_id": user_id})
        item = response.get("Item", {})
        current_balance = item.get("balance", 0)
        portfolio = item.get("portfolio", {})

        # Check if user has enough shares to sell
        if symbol not in portfolio or portfolio[symbol] < shares:
            raise ValueError("Insufficient shares")

        # Update the user's balance and portfolio
        new_balance = current_balance + shares * price
        portfolio[symbol] = portfolio[symbol] - shares
        if portfolio[symbol] == 0:
            del portfolio[symbol]
        table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set balance=:b, portfolio=:p",
            ExpressionAttributeValues={
                ":b": new_balance,
                ":p": portfolio
            }
        )

    return {"message": "Stock transaction successful"}
