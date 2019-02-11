# Design question
## Requirements
- Monitor simultaneously from different geo-locations
- Single output report

## Simple solution
The current monitor can be used as a distributed monitoring tool with some modifications. 

- Input: We can save the configutation in a remote accessible resource to the monitor like a database or storage solution
- fmonitor: Add feature to load configutation from outside location and log results to outside service.
- Output: Instead of saving the result in `stdout` we should use a centralized location like an elasticsearch instance (Need to tag results with geolocation for analysis)

## What about security?
monitor deals with both input and output services over network, if we imagine for example that our config file is in an S3 bucket and we output results to an elasticsearch instance:
- Use `IAM policies` to configure access to the config file, monitor itself needs read only.
- Network communication should only be over SSL/TLS encryption
- Enable Authentication on elasticsearch instance
- Follow security practices on EC2/ECS or any other plaform where monitor is deployed


## Millions of websites to monitor ?
If there is a big enough workload on the monitor we could have a less than optimal performance, even though we are using currenlty worker threads to help cycle the CPU when performing I/O work it would be better to switch to an asynchronous solution, either with python build in `async` model or use different solution based on `nodejs` or `golang` ...
