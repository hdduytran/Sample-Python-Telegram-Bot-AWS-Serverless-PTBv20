import boto3
import json

lambda_client = boto3.client('lambda')

def invoke_lambda(function_name, payload):
    """
    Invoke a Lambda function with the given payload.
    
    Args:
        function_name (str): The name of the Lambda function to invoke.
        payload (dict): The payload to send to the function.
    
    Returns:
        dict: The response from the Lambda function.
    """
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload)
    )
    return json.loads(response['Payload'].read().decode('utf-8'))