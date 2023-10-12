import os
import boto3
from datetime import datetime, timedelta

# Set your AWS credentials as environment variables
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIARWCTPADXXM6BOGUA'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'BO+7r0vPZ5igYAS/Ybt+Owvx/DPA304x7oNtdeOs'
os.environ['AWS_REGION'] = 'ap-south-1'

def get_rds_instances_by_tags(tag_key, tag_value):
    # Create an RDS client
    rds_client = boto3.client('rds')

    # Describe all RDS instances
    response = rds_client.describe_db_instances()

    instances = []

    for instance in response['DBInstances']:
        # Fetch tags for the instance
        instance_tags = rds_client.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])['TagList']

        # Check if the specified tag key and value exist for the instance
        if any(tag['Key'] == tag_key and tag['Value'] == tag_value for tag in instance_tags):
            instance_info = {
                'DBInstanceIdentifier': instance['DBInstanceIdentifier'],
                'DBInstanceClass': instance['DBInstanceClass'],
                'DBInstanceStatus': instance['DBInstanceStatus'],
                'Tags': instance_tags
            }
            instances.append(instance_info)

    return instances

def get_rds_cpu_utilization(db_instance_identifier, start_time, end_time):
    cloudwatch_client = boto3.client('cloudwatch')

    # Get CPU utilization metrics data
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'DBInstanceIdentifier',
                'Value': db_instance_identifier
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,  # 5-minute intervals
        Statistics=['Average'],
        Unit='Percent'
    )

    return response['Datapoints']

def get_rds_cost(db_instance_identifier, start_time, end_time):
    # Create a Cost Explorer client
    ce_client = boto3.client('ce')
    rds_client = boto3.client('rds')
    instance_tags = rds_client.list_tags_for_resource(ResourceName=f"arn:aws:rds:ap-south-1:116139163887:db:{db_instance_identifier}")['TagList']

    # Get cost data
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_time.strftime('%Y-%m-%d'),
            'End': end_time.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        Filter={
            'Dimensions': {
                'Key': 'INSTANCE_TYPE',
                'Values': [f'{tag["Value"]}' for tag in instance_tags if tag["Key"] == tag_key]
            }
        }
    )

    return response['ResultsByTime']

if __name__ == '__main__':
    # Replace 'YourTagKey' and 'YourTagValue' with the actual key and value of the tags
    tag_key = 'mc'
    tag_value = 'stan'

    rds_instances = get_rds_instances_by_tags(tag_key, tag_value)


    if rds_instances:
        print("RDS Instances:")
        for rds_instance in rds_instances:
            print(f"DB Instance Identifier: {rds_instance['DBInstanceIdentifier']}")
            print(f"DB Instance Class: {rds_instance['DBInstanceClass']}")
            print(f"DB Instance Status: {rds_instance['DBInstanceStatus']}")
            print(f"Tags: {rds_instance['Tags']}")

            # Get CPU Utilization metrics
            print("\nCPU Utilization Metrics:")
            start_time1 = datetime.utcnow() - timedelta(hours=6)  # Last 6 hours
            end_time1 = datetime.utcnow()
            metrics_data = get_rds_cpu_utilization(rds_instance['DBInstanceIdentifier'], start_time1, end_time1)

            for datapoint in metrics_data:
                timestamp = datapoint['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                value = datapoint['Average']
                print(f"{timestamp} - CPU Utilization: {value}%")

            print("-----")

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=1)

            # Get and print cost data
            cost_data = get_rds_cost(rds_instance['DBInstanceIdentifier'], start_time, end_time)

            print(f"Cost data for DB instance {rds_instance['DBInstanceIdentifier']} from {start_time} to {end_time}:")
            print(cost_data)
            for result in cost_data:
                timestamp = result['TimePeriod']['Start']
                value = result['Total']['UnblendedCost']['Amount']
                print(f"{rds_instance['DBInstanceIdentifier']} - {timestamp} - Cost: ${value}")

            print("-----")
    else:
        print("No RDS instances found with the specified tags.")
