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

def delete_volumes(client):
    #Filter out only available volumes, as those that are in-use will be deleted when the instance is terminated.
    response = client.describe_volumes(
    Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    available_volumes = response["Volumes"]

    for volume in available_volumes:
        client.delete_volume(VolumeId=volume["VolumeId"])
        print(volume["VolumeId"], "deleted.")

def release_elastic_ips(client):
    response = client.describe_addresses()
    print("RESPONSE:", response)
    addresses = response["Addresses"]

    for address in addresses:
        #if "Tags" in address:
            #for tag in address["Tags"]:
                #if tag["Value"] == "Project: Finance Audit":
        if "AssociationId" not in address:
            client.release_address(AllocationId=address["AllocationId"])
        print(address["PublicIp"], "released.")


def lambda_handler(event, context):
    ec2 = boto3.client("ec2")
    sns = boto3.client("sns")
    terminate_instances(ec2)
    delete_volumes(ec2)
    release_elastic_ips(ec2)
    sns.publish(
        TopicArn="arn:aws:sns:us-east-1:963527046541:TerminateWaste",
        Message="All instances tagged with 'Project: Finance Audit' have been terminated.",
        Subject="Finance Audit Resource Termination"
    )
