import boto3
from datetime import datetime, timedelta

# Replace with your AWS credentials and region
aws_access_key_id = 'AKIARWCTPADXXM6BOGUA'
aws_secret_access_key = 'BO+7r0vPZ5igYAS/Ybt+Owvx/DPA304x7oNtdeOs'
aws_region = 'ap-south-1'  # Replace with your AWS region

# Initialize the AWS Cost Explorer client with your credentials and region
ce = boto3.client(
    'ce',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Define a function to get AWS Cost Explorer cost data for a specific month
def get_monthly_cost(start_date, end_date):
    response_ce = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d'),
        },
        Granularity='MONTHLY',
        Metrics=['BlendedCost'],
    )

    for result in response_ce['ResultsByTime']:
        print(f"Time Period: {result['TimePeriod']['Start']} to {result['TimePeriod']['End']}, Cost: {result['Total']['BlendedCost']['Amount']} {result['Total']['BlendedCost']['Unit']}")

# Fetch AWS Cost Explorer cost data for the current month
today = datetime.utcnow()
start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
get_monthly_cost(start_of_month, today)

# Define the number of previous months to fetch data for
num_previous_months = 2  # You can change this to the desired number of previous months

# Fetch AWS Cost Explorer cost data for the previous months using a loop
for i in range(1, num_previous_months + 1):
    start_date = (start_of_month - timedelta(days=1)).replace(day=1)
    end_date = start_of_month - timedelta(days=1)
    get_monthly_cost(start_date, end_date)
    start_of_month = start_date

