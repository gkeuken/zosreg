# zosreg
Centralized Software Registry via Python and Dictionaries

Functions/Features:
- Read an SMPE CSI, or a list of SMPE CSI's and produce a consolidated "Registry" of software within a Python Dictionary.
- Search the Registry for software 
- Add custom (non-smpe) software to the Registry
- Print Summary information about all software in the Registry
- Easily find all the FMID's for any given product
- Easily search for SYSMODS and see where/if they are installed
This repo is meant to be cloned directly to z/OS.


Requirements:
- Read access to SMPE CSI's you intend to use to populate registry
- Write access to make new directory /var/zosreg or alternatively you can use alternate Registry directory via -r
- Python with pyyaml and jinja2 (pip install pyyaml, pip install jinja2)
- Sufficient space in /var to hold the generated dictionaries and SMPE data, or add new filesystem
- This utility will create a new directory /var/zosreg to hold the dictionaries and smpe data.
- If you have a large amount of CSI's, or very small /var you should define and mount a new filesystem at /var/zosreg or use alternate directory with -r


Running:
Populating or refreshing the Registry:
-  Copy smpetemplate.yaml file to a user directory and update with the SMPE CSI's you wish to add. You will specify this customized /directory/file when running generation option -g
-  The REXX DATA section should be ok as is but verify/update as needed.
-  Run: zosreg.py -g customized_file
- Generally you only need to do this at initial setup or anytime you wish to refresh the Registry - say you add/delete new CSI's or you want to refresh the Registry with updated info from your CSI's

Run zosreg.py -h to get help

Searching for Features/products:
-  Run: zosreg.py -s search_keyword

Searching for SYSMODS:
-  Run zosreg.py -q sysmod_name
You can search for SYSMODS matching a prefix simply by specifying only part of the SYSMOD name, for example: UI940 would search for all sysmods having this prefix.

Pointing to alternate Registry:
-  zosreg.py -r alternate_directory_name

Adding custom Registry Entries:
-  Run zosreg.py -a  (for prompted inputs)
-  Or  zosreg.py -a -i input_yaml  (for using yaml input file)
Note that custom Registry Entries are meant for NON-SMPE installed software. If software is installed via SMPE then add the CSI to the smpetemplate.yaml file and run zosreg.py -z


As mentioned above, the default location for the Registry is /var/zosreg.
You can create and query from alternate Registry locations by using -r registry_directory_name
- For example:
   - zosreg.py -z -r /var/altreg   (to generate a new Registry at /var/altreg)
   -  zosreg.py -p -r /var/altreg   (to get summary of products in the alternate registry)
