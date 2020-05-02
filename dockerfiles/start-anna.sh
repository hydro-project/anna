#!/bin/bash

#  Copyright 2018 U.C. Berkeley RISE Lab
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

if [ -z "$1" ]; then
  echo "No argument provided. Exiting."
  exit 1
fi

# A helper function that takes a space separated list and generates a string
# that parses as a YAML list.
gen_yml_list() {
  IFS=' ' read -r -a ARR <<< $1
  RESULT=""

  for IP in "${ARR[@]}"; do
    RESULT=$"$RESULT        - $IP\n"
  done

  echo -e "$RESULT"
}

cd $HYDRO_HOME/anna
mkdir -p conf

# Check if the context that we are running in is EC2 or not. If it is, we
# determine separate private and public IP addresses. Otherwise, we use the
# same one for both.
IS_EC2=`curl -s http://169.254.169.254`
PRIVATE_IP=`ifconfig eth0 | grep 'inet addr:' | grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1 }'`
if [[ ! -z "$IS_EC2" ]]; then
  PUBLIC_IP=`curl http://169.254.169.254/latest/meta-data/public-ipv4`
else
  PUBLIC_IP=$PRIVATE_IP
fi

# Download latest version of the code from relevant repository & branch -- if
# none are specified, we use hydro-project/anna by default.
git remote remove origin
if [[ -z "$REPO_ORG" ]]; then
  REPO_ORG="hydro-project"
fi

if [[ -z "$REPO_BRANCH" ]]; then
  REPO_BRANCH="master"
fi

git remote add origin https://github.com/$REPO_ORG/anna
while ! (git fetch -p origin)
do
  echo "git fetch failed, retrying"
done
git checkout -b brnch origin/$REPO_BRANCH
git submodule sync
git submodule update

# Compile the latest version of the code on the branch we just check out.
cd build && make -j2 && cd ..

# Do not start the server until conf/anna-config.yml has been copied onto this
# pod -- if we start earlier, we won't now how to configure the system.
while [[ ! -f "conf/anna-config.yml" ]]; do
  continue
done

# Tailor the config file to have process specific information.
if [ "$1" = "mn" ]; then
  echo -e "monitoring:" >> conf/anna-config.yml
  echo -e "    mgmt_ip: $MGMT_IP" >> conf/anna-config.yml
  echo -e "    ip: $PRIVATE_IP" >> conf/anna-config.yml

  ./build/target/kvs/anna-monitor
elif [ "$1" = "r" ]; then
  echo -e "routing:" >> conf/anna-config.yml
  echo -e "    ip: $PRIVATE_IP" >> conf/anna-config.yml

  LST=$(gen_yml_list "$MON_IPS")
  echo -e "    monitoring:" >> conf/anna-config.yml
  echo -e "$LST" >> conf/anna-config.yml

  ./build/target/kvs/anna-route
elif [ "$1" = "b" ]; then
  echo -e "user:" >> conf/anna-config.yml
  echo -e "    ip: $PRIVATE_IP" >> conf/anna-config.yml

  LST=$(gen_yml_list "$MON_IPS")
  echo -e "    monitoring:" >> conf/anna-config.yml
  echo -e "$LST" >> conf/anna-config.yml

  LST=$(gen_yml_list "$ROUTING_IPS")
  echo -e "    routing:" >> conf/anna-config.yml
  echo -e "$LST" >> conf/anna-config.yml

  ./build/target/benchmark/anna-bench
else
  echo -e "server:" >> conf/anna-config.yml
  echo -e "    seed_ip: $SEED_IP" >> conf/anna-config.yml
  echo -e "    public_ip: $PUBLIC_IP" >> conf/anna-config.yml
  echo -e "    private_ip: $PRIVATE_IP" >> conf/anna-config.yml
  echo -e "    mgmt_ip: $MGMT_IP" >> conf/anna-config.yml

  LST=$(gen_yml_list "$MON_IPS")
  echo -e "    monitoring:" >> conf/anna-config.yml
  echo -e "$LST" >> conf/anna-config.yml

  LST=$(gen_yml_list "$ROUTING_IPS")
  echo -e "    routing:" >> conf/anna-config.yml
  echo -e "$LST" >> conf/anna-config.yml

  ./build/target/kvs/anna-kvs
fi
