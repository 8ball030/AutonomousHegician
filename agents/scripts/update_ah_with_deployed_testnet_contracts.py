import yaml


def get_new_addresses(config_path = "./hegic_deployer/contract_config.yaml"):
    with open(config_path, "r") as f:
        addresses = yaml.safe_load(f)
    return addresses


def get_ah_configuration(config_path = "./autonomous_hegician/skills/option_management/skill.yaml"):
    
    with open(config_path, "r") as f:
        agent_config = yaml.safe_load(f)
    return agent_config


from copy import deepcopy

def update_ah_config_with_new_config(agent_config, addresses):
    new_config = deepcopy(agent_config)
    new_config['models']['strategy']['args'] = addresses
    return new_config



def write_new_config_to_ah(new_config, config_path = "./autonomous_hegician/skills/option_management/skill.yaml"):
    with open(config_path, "w") as f:
        yaml.safe_dump(new_config, f)



def do_work():
    agent_config = get_ah_configuration()
    addresses = get_new_addresses()
    new_agent_config = update_ah_config_with_new_config(agent_config, addresses)
    write_new_config_to_ah(new_agent_config)
    print("Configurations copied.")
    
if __name__ == "__main__":
    do_work()