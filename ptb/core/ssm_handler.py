import boto3

# Initialize the SSM client
ssm_client = boto3.client('ssm')

def get_parameter(parameter_name):
    """
    Get the value of an SSM parameter.
    
    Args:
        parameter_name (str): The name of the parameter to retrieve.
    
    Returns:
        str: The value of the parameter.
    """
    response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']

def update_parameter(parameter_name, new_value):
    """
    Update the value of an SSM parameter.
    
    Args:
        parameter_name (str): The name of the parameter to update.
        new_value (str): The new value for the parameter.
    
    Returns:
        dict: Information about the updated parameter.
    """
    response = ssm_client.put_parameter(
        Name=parameter_name,
        Value=new_value,
        Type='String',
        Overwrite=True
    )
    return response

# Example usage
if __name__ == "__main__":
    parameter_name = '/steath_writer_cookies'
    
    # Get the current value of the parameter
    current_value = get_parameter(parameter_name)
    print("Current value:", current_value)
    
    # Update the parameter value
    new_value = input("Enter new value for the parameter: ")
    update_response = update_parameter(parameter_name, new_value)
    print("Parameter updated successfully:", update_response)
