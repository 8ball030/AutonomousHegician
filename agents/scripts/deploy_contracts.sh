#!/bin/sh
cd hegic_deployer
aea install
aea build
aea issue-certificates
aea run
