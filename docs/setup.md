# Setup of Project

- Flash a raspberry pi image using balenEthcher

- update the allowed hosts

- enable ssh access


# 

create the following files in the boot drive
[wpa_supplicant.conf](https://gist.github.com/anshulkhare7/fdd662c358a2ff7eba48fd11050b9243)
touch ssh.txt

update the ./ssh/authorized_hosts

update hostname
sudo hostnamectl set-hostname autonomous_hegician

# update and upgrade

 sudo apt-get update; sudo apt-get upgrade -y
 sudo apt-get install git -y

# install docker
 curl -fsSL https://get.docker.com -o get-docker.sh 
 sudo sh get-docker.sh
 rm get-docker.sh
 
 # update permission to make easier to run
 sudo usermod -aG docker pi
 
 docker version
 
 # create sshkey
 ssh-keygen -t rsa -b 4096 -C "tomrae030@hotmail.com"
 
 # install python

 sudo apt-get install python3 python3-pip -y

  # install deps 
 sudo apt-get install py-pip python3-dev libffi-dev openssl-dev gcc libc-dev make -y 
# install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo  pip3 install docker-compose
 
 # To run
 ``` #bash#
 cd AutonmousHegician;
 docker-compose up
 ```
 # To run tests
 Due to the transactional nature of the of the application and the behavioural nature of the agent, we perform a number of integration tests.
 
 The initial test is to configure the local blockchain which will allow the user to perform local testing before the deployment to a live environment.
 # To setup on local test net
 ``` ## bash ##
 cd hegic_contracts
 python3 
 ```
 
 
 # To setup to run on live chain
 
 # To setup to run on ropsten
 
 

