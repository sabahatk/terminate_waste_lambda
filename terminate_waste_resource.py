import json
import boto3

def terminate_instance(client, instance_id):
    response = client.terminate_instances(
        InstanceIds=[
            instance_id,
        ],
    )
    
    print(instance_id, "terminated.")
    
def terminate_instances(client):
    response = client.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            if "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Value"] == "Project: Finance Audit" and instance["State"]["Name"] != "terminated":
                        terminate_instance(client, instance["InstanceId"])

'''def terminate_volumes(client):
    ec2 = boto3.resource("ec2")
    #Filter out only available volumes, as those that are in-use will be deleted when the instance is terminated.
    available_volumes = ec2.volumes.filter(
    Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    for volume in available_volumes:
        volume.delete()
        print(volume["VolumeId"], "deleted.")'''

def lambda_handler(event, context):
    ec2 = boto3.client("ec2")
    sns = boto3.client("sns")
    terminate_instances(ec2)
    #terminate_volumes(ec2)
    sns.publish(
        TopicArn="arn:aws:sns:us-east-1:963527046541:TerminateWaste",
        Message="All instances tagged with 'Project: Finance Audit' have been terminated.",
        Subject="Finance Audit Resource Termination"
    )