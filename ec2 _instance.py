import os
import boto3
from datetime import datetime, timedelta

# Set your AWS credentials as environment variables
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIARWCTPADXXM6BOGUA'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'BO+7r0vPZ5igYAS/Ybt+Owvx/DPA304x7oNtdeOs'
os.environ['AWS_REGION'] = 'ap-south-1'

def get_instances_by_tags(tag_key, tag_value):
    # Create an EC2 client
    ec2_client = boto3.client('ec2')
    
    # Describe instances based on tags
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            }
        ]
    )

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_info = {
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name'],
                'Tags': instance.get('Tags', [])
            }
            instances.append(instance_info)

    return instances

def get_ec2_metrics(instance_id, metric_name, start_time, end_time):
    cloudwatch_client = boto3.client('cloudwatch')

    # Get metrics data
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName=metric_name,
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,  # 5-minute intervals
        Statistics=['Average'],
        Unit='Percent'  # Or other units based on the metric
    )

    return response['Datapoints']

def get_cost_for_instance(instance_type, start_time, end_time):
    # Create a Cost Explorer client
    ce_client = boto3.client('ce')

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
                'Values': [instance_type]
            }
        }
    )

    return response['ResultsByTime']

if __name__ == '__main__':
    # Replace 'YourTagKey' and 'YourTagValue' with the actual key and value of the tags
    tag_key = 'mc'
    tag_value = 'stan'

    instances = get_instances_by_tags(tag_key, tag_value)

    if instances:
        print("Instances:")
        for instance in instances:
            print(f"Instance ID: {instance['InstanceId']}")
            print(f"Instance Type: {instance['InstanceType']}")
            print(f"State: {instance['State']}")
            print(f"Tags: {instance['Tags']}")

            # Get CPU Utilization metrics
            print("\nCPU Utilization Metrics:")
            start_time1 = datetime.utcnow() - timedelta(hours=6)  # Last 6 hours
            end_time1 = datetime.utcnow()
            metrics_data = get_ec2_metrics(instance['InstanceId'], 'CPUUtilization', start_time1, end_time1)

            for datapoint in metrics_data:
                timestamp = datapoint['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                value = datapoint['Average']
                print(f"{timestamp} - CPU Utilization: {value}%")

            print("-----")

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)

            # Get and print cost data
            cost_data = get_cost_for_instance(instance['InstanceType'], start_time, end_time)

            print(f"Cost data for instance {instance['InstanceId']} from {start_time} to {end_time}:")

            for result in cost_data:
                timestamp = result['TimePeriod']['Start']
                value = result['Total']['UnblendedCost']['Amount']
                print(f"{instance['InstanceId']} - {timestamp} - Cost: ${value}")

            print("-----")
    else:
        print("No instances found with the specified tags.")

