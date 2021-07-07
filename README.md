# Backup Uploader

A simple command that uploads files, with a focus on backup files, to a cloud server, allowing to have different directories that store backups with different retain policies.

## Backup Chain

A chain is composed of several directories, which can be an Intermediary or a Last directory.

An Intermediary directory has 4 parameters:

- Name: Of the directory
- Strftime Format: The [strftime](https://strftime.org/) datetime format used to generate the filename of a new file moved into the directory.
- Capacity: How many files can be stored in this directory
- Counter Max: Maximum value of the directory internal counter.

A Last directory needs only the first 2 parameters (Name and Strftime Format). A chain can only have one Last directory.

Whenever a new file is uploaded to a directory and its capacity is exceeded, its counter is incremented. If the counter didn't reach its maximum the oldest file on the target directory is deleted, else the counter is reset and the oldest file is moved to the next directory in the chain. Once a Last directory is reached no more moving occurs for that file. For that, a Last directory has no capacity. If no Last directory is defined, after the last Intermediary directory, files are deleted instead of being moved to a Last directory.

For example, we can have three directories: week, month, olds.

- week: Here are stored up to seven files, the backups of the last 7 days
- month: After the week directory is full, every 7 days the oldest backup is moved to this month directory and the other days the backup is discarded. If we set the maximum files for this directory to 4, we will end up with a backup per week of the last month.
- olds: From the month directory we intend to preserve only one per month. We can then make this directory the last of the chain and will not have a maximum capacity.

## Install

1. Install the python package
   
   `pip install backup_uploader`
   
   Since each cloud server has a different upload API, you will also need to install a python client of the target cloud server.
   
   You can install them along with this package like this `pip install backup_uploader[dropbox]`. Use the value of the Server Argument point on the [Supported Servers](#supported-servers) section of the target cloud server.

2. Create the counters directory
   
   ```shell
   sudo sh -c "useradd backup_uploader && mkdir /var/lib/backup_uploader && chown backup_uploader:backup_uploader /var/lib/backup_uploader"
   ```

## Usage

This package makes an executable `backup_uploader` available that expects 5 required positional arguments.

- **Application Name**
  
  This is mainly used to create a root directory on places that can be shared with other applications.

- **Server**
  
  To where the file will be uploaded. Check the [Supported Servers](#supported-servers) section to see the available options for this field.

- **Path to the Credentials File**
  
  The structure of this file depends on the Server to where the file will be uploaded, for that, check the instructions in [Supported Servers](#supported-servers) for the chosen server.

- **Backup Chain Config**
  
  Specification of the several directories and their configurations. Defined as a string where each directory config is separated by `;` and each directory config parameter is separated by `:`. As an example, for the example provided at the beginning of this README the config is
  
  ```textile
  week:%Y%d:7:7;month:%Y%W:4:1;olds:%Y%W
  ```

- **Path to the File To Upload**

Example:

```shell
backup_uploader website_backups dropbox creadentials.txt "week:%d:7:7;other;%d" backup.tar.gz
```

**Important notes:**

1. to ensure that the script can access the counters directory this script should be run by a user that belongs to the `backup_uploader` group.

2. the Backup Chain Config argument must be within quotation marks so the shell doesn't interpret the `;` symbol as a separation between commands

## Supported Servers

### Dropbox

You will need to create a Dropbox app and add the `files.content.write` permissions under the Permissions Tab of your Dropbox App.

- Server argument
  
  `dropbox`

- Credentials file format
  
  Text file with the [app token](https://dropbox.tech/developers/generate-an-access-token-for-your-own-account)

- Where are the files stored?
  
  Each backup application will create a directory on the root of your app's directory with the name of the Application Name argument.

- Python client
  
  [dropbox](https://pypi.org/project/dropbox/)

### Mega

- Server argument
  
  `mega`

- Credentials file format
  
  Text file with two lines.
  
  1. Email of the mega account
  
  2. Password of the mega account
  
  ```textile
  user@mail.com
  password
  ```

- Where are files stored?
  
  Each backup application will create a directory on the root of your mega drive with the name of the Application Name argument.

- Python client
  
  [mega.py](https://pypi.org/project/mega.py/)
