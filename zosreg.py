"""
  Register z/OS products
"""
import sys
import os
import tempfile
import subprocess
import re
import argparse
import yaml
import jinja2


def pr_red(prt):
    """
    function prints text in Red.
    """
    print(f"\033[91m {prt}\033[00m")


def pr_cyan(prt):
    """
    You won't believe it possible, but, this prints text in Cyan... really it does.
    """
    print(f"\033[96m {prt}\033[00m")


def parse_arguments(argv=None):
    """
    Parse program arguments
    """
    program_name = os.path.basename(sys.argv[0])
    program_dir_name = os.path.dirname(sys.argv[0])
    if program_dir_name == '':
        program_dir_name = '.'
    if argv is None:
        argv = sys.argv[1:]
    try:
        parser = argparse.ArgumentParser(program_name)
        parser.add_argument("-a", "--add",action="store_true",
                            help="Add a NON-SMPE Feature/Product to the Registry",
                            required=False)
        parser.add_argument("-d", "--debug",action="store_true",
                            help="Turn on debug output",
                            required=False)
        parser.add_argument("-f", "--feature",
                            help="Show details for specific feature.",
                            required=False)
        parser.add_argument("-g", "--generate_template",
                            help="Generate/Regenerate the SMPE Repository Dictonaries \
                                  using SMPE LIST data reports. Specify Template directory/name",
                            required=False)
        parser.add_argument("-i", "--input",
                            help="Yaml input file to use with -a. If -i not used then \
                                    input must be entered at terminal",
                            required=False)
        parser.add_argument("-j", "--fmidptfs",
                            help="List of ptfs for a given fmid, \
                                    specify a valid fmid in Registry",
                            required=False)
        parser.add_argument("-l", "--listzones",choices=['zone','fmids'],
                            help="List of zones and fmids in Registry, either specify zone or \
                                    specify fmids to get both zones and all fmids",
                            required=False)
        parser.add_argument("-p", "--summary",action="store_true",
                            help="Print Summary of the Features/Products in the Registry",
                            required=False)
        parser.add_argument("-q", "--sysmods",
                            help="Search for SYSMODs (PTFs, FUNCTIONs)",
                            required=False)
        parser.add_argument("-r", "--registry",
                            help="Use alternate Registry directory \
                                    Default is /var/zosreg",
                            required=False)
        parser.add_argument("-s", "--search",
                            help="Search the Registry (FMIDs, PIDs, Description text)",
                            required=False)
        parser.add_argument("-z", "--zone",
                            help="Zone search/print",
                            required=False)

        progargs = parser.parse_args(argv)
        progargs.PRODREG = 'Product-Registration-Data'
        progargs.SMPETEMPLATE_YAML = progargs.generate_template
        progargs.SMPEREGDIR = '/var/zosreg'
        if progargs.registry:
            progargs.SMPEREGDIR = progargs.registry
        progargs.SMPEDATA_OUTPUT = f'{progargs.SMPEREGDIR}/smpedata.txt'
        progargs.SMPESYSMDB = f'{progargs.SMPEREGDIR}/smpesym.yaml'
        progargs.SMPOUT  = f'{progargs.SMPEREGDIR}/smpout.txt'
        progargs.SMPLOGA  = f'{progargs.SMPEREGDIR}/smploga.txt'
        progargs.SMPLOG  = f'{progargs.SMPEREGDIR}/smplog.txt'
        progargs.SMPEREGDB  = f'{progargs.SMPEREGDIR}/smpereg.yaml'
        progargs.CUSTREGDB  = f'{progargs.SMPEREGDIR}/custreg.yaml'
        progargs.PROCIND = ''

    except argparse.ArgumentError as ae:
        print(ae)
    except argparse.ArgumentTypeError as aef:
        print(aef)

    return progargs

def cust_add(update_dict):
    """
    Add product registration records
    """
    # Check if customer reg DB exists and if not initialize empty one
    with open(PARGS.CUSTREGDB, 'a+', encoding='utf8') as new_regdata:
        new_regdata.seek(0)
        if not new_regdata.read(1):
            pr_red('Customer Registry not found, initializing new Customer Registry')
            reg_data = {}
            reg_data[PARGS.PRODREG] = {}
            yaml.dump(reg_data, new_regdata, default_flow_style=False)

    reg_data = load_dict(PARGS.CUSTREGDB)

    if not update_dict:
        pr_red('No input yaml specified, enter Customer data via following prompts')
        tdict = {}
        product = input('Product ==> ')
        tdict[product] = {}
        tdict[product]['fmids'] = input('Fmids ==> ')
        tdict[product]['name'] = input('Name ==> ')
        tdict[product]['version'] = input('Version ==> ')
        tdict[product]['pid'] = input('Pid ==> ')
        reg_data[PARGS.PRODREG].update(tdict)
    else:
        pr_cyan(f'Adding input yaml {update_dict} to Customer Registry')
        reg_data[PARGS.PRODREG].update(update_dict)

    with open(PARGS.CUSTREGDB, 'w', encoding='utf8') as new_regdata:
        yaml.dump(reg_data, new_regdata, default_flow_style=False)
    print(f'Customer Registry updated {PARGS.CUSTREGDB}')

def prod_update():
    """
    Update product registration record
    """

def prod_delete():
    """
    Delete product registration record
    """

def prod_key_add():
    """
    Add key to product registration dictionary
    """

def load_dict(input_yaml):
    """
    Load dictionary
    """
    try:
        with open(input_yaml, 'r', encoding='utf8') as reg_yaml:
            _regdata = yaml.safe_load(reg_yaml)
        return _regdata
    except Exception:
        print(f'Exception on dictionary {input_yaml}',flush=True)
        return None

def prod_search(reg_data,search_txt):
    """
    Search registration dictionary for key
    """
    search_str = re.compile(search_txt, re.I)

    print('   Feature    Description                                              '\
           'PID        Version')
    print('  --------------------------------------------------------------------'\
           '-------------------')
    for products in reg_data[PARGS.PRODREG]:
        if re.search(search_str,products) or \
        re.search(search_str,reg_data[PARGS.PRODREG][products]['name']) or \
        re.search(search_str,reg_data[PARGS.PRODREG][products]['pid']):
            pr_cyan(f"  {products:9}" +\
                  f"  {reg_data[PARGS.PRODREG][products]['name']:55}" +\
                  f"  {reg_data[PARGS.PRODREG][products]['pid']:9}" +\
                  f"  {reg_data[PARGS.PRODREG][products]['version']:10}")
        for _fmid in reg_data[PARGS.PRODREG][products]['fmids']:
            if re.search(search_str,_fmid):
                pr_cyan(f"  {products:9}" +\
                      f"  {reg_data[PARGS.PRODREG][products]['name']:55}" +\
                      f"  {reg_data[PARGS.PRODREG][products]['pid']:9}" +\
                      f"  {reg_data[PARGS.PRODREG][products]['version']:10}")

def get_smpe_data(data_type):
    """
    Run SMPE LISTFEAT to get data
    """
    PARGS.PROCIND = f'\033[91m Gathering SMPE {data_type} info .'
    templated_yaml = ''
    subprocess.run(['rm', '-rf', PARGS.SMPEDATA_OUTPUT],capture_output=False,check=False)
    smpetemp_yaml = load_dict(PARGS.SMPETEMPLATE_YAML)
    for csiname in smpetemp_yaml['CSILIST']['CSIS']:
        if 'FEATURE' in data_type:
            templated_yaml = template_rexx(csiname,'FEATURE')
        else:
            templated_yaml = template_rexx(csiname,'GLOBALZONE ALLZONES SYSMODS')
        loaded_temp_yaml = yaml.safe_load(templated_yaml)
        run_rexx(loaded_temp_yaml)
        if data_type == 'SYSMODS':
            ptfdict = gen_csi_dict(csiname)
            gen_fmid_sysmod_dict(csiname,ptfdict)
            subprocess.run(['rm', '-rf', PARGS.SMPEDATA_OUTPUT],capture_output=False,check=False)


def gen_zonelist_output(list_type):
    """
    Print all zones in Registry
    """
    sysmod_dict = load_dict(PARGS.SMPESYSMDB)
    print(f'Zone List')
    for csis in sysmod_dict:
        pr_red(f'CSI: {csis}')
        for zones in sysmod_dict[csis]:
            pr_cyan(f'     ZONE: {zones}')
            if list_type == 'fmids':
                for fmids in sysmod_dict[csis][zones]:
                    pr_cyan(f'        FMID: {fmids}')


def gen_fmidptfs_output(srcstr):
    """
    Print sysmod info for a given fmid
    """
    sysmod_dict = load_dict(PARGS.SMPESYSMDB)
    found_sysmod=False
    for csis in sysmod_dict.keys():
        for zone in sysmod_dict[csis]:
            if srcstr in sysmod_dict[csis][zone]:
                pr_cyan(f'The following SYSMODS found for FMID {srcstr} in ZONE {zone}')
                found_sysmod=True
                for ptfs in sysmod_dict[csis][zone][srcstr]:
                    print(f'{ptfs} - TYPE: {sysmod_dict[csis][zone][srcstr][ptfs]["Type"]}\
                          STATUS: {sysmod_dict[csis][zone][srcstr][ptfs]["Status"]}')
    if not found_sysmod:
        pr_red(f'No SYSMOD(s) found for FMID: {srcstr}')

def gen_sysmods_zone_output(srcstr):
    """
    Print sysmod info for a given zone
    """
    sysmod_dict = load_dict(PARGS.SMPESYSMDB)
    found_sysmod=False
    for csis in sysmod_dict.keys():
        if srcstr in sysmod_dict[csis]:
            pr_cyan(f'The following SYSMODS found for zone {srcstr} in CSI {csis}')
            found_sysmod=True
            for fmid in sysmod_dict[csis][srcstr]:
                for ptfs in sysmod_dict[csis][srcstr][fmid]:
                    print(ptfs,sysmod_dict[csis][srcstr][fmid][ptfs]['Type'],
                          sysmod_dict[csis][srcstr][fmid][ptfs]['Status'])
        if not found_sysmod:
            if PARGS.debug:
                print(f'***  SYSMOD {srcstr} not found in CSI: {csis}, continuing search')
    if not found_sysmod:
        pr_red(f'No SYSMOD(s) {srcstr} found in any known CSI')



def gen_sysmods_output(srcstr):
    """
    Print sysmod info
    """
    sysmod_dict = load_dict(PARGS.SMPESYSMDB)
    feat_dict = load_dict(PARGS.SMPEREGDB)
    found_sysmod=False
    for csis in sysmod_dict.keys():
        for zone in sysmod_dict[csis]:
            for fmid in sysmod_dict[csis][zone]:
                for ptfs in sysmod_dict[csis][zone][fmid]:
                    if srcstr in ptfs:
                        pr_red(f'Entry {ptfs} found:')
                        pr_cyan(f'    CSI       : {csis}')
                        pr_cyan(f'    Zone:     : {zone}')
                        fmidstr = f'    FMID:     : {fmid} ('
                        for feats in feat_dict[PARGS.PRODREG]:
                            if fmid in feat_dict[PARGS.PRODREG][feats]['fmids']:
                                fmidstr+= "".join(f"{feat_dict[PARGS.PRODREG][feats]['name']}")
                                fmidstr+= "".join(f":{feat_dict[PARGS.PRODREG][feats]['pid']}")
                                fmidstr+= "".join(f":{feat_dict[PARGS.PRODREG][feats]['version']}, ")
                        pr_cyan(f'{fmidstr})')
                        for ditems in sysmod_dict[csis][zone][fmid][ptfs]:
                            pr_cyan(f"    {ditems.ljust(9)} : "\
                                    f"{sysmod_dict[csis][zone][fmid][ptfs][ditems]}")
                        print(' ')
                        found_sysmod=True
        if not found_sysmod:
            if PARGS.debug:
                print(f'***  SYSMOD {srcstr} not found in CSI: {csis}, continuing search')
    if not found_sysmod:
        pr_red(f'No SYSMOD(s) {srcstr} found in any known CSI')


def gen_csi_dict(csiname):
    """
    Generate CSI and ZONE Dictionary Structure
    Dict Structure:
    CSI:
       ZONE:
           FMID:
                - SYSMOD1
                - SYSMOD2
    """
    _ptfdict = {}
    zone = ''
    xline = 1
    yline = 50000
    _ptfdict[csiname] = {}
    with open(PARGS.SMPEDATA_OUTPUT, 'r', encoding='cp1047') as smpein:
        for lines in smpein:
            if 'FILE ALLOCATION REPORT' in lines:
                break
            xline+=1
            if xline%yline == 0:
                PARGS.PROCIND+="".join('.')
                print(f'\r{PARGS.PROCIND}',end='')
            if lines[64:73] == 'PROCESSED' and '.CSI' in lines:
                zone = lines[1:9].strip()
                _ptfdict[csiname][zone] = {}
                continue
    if PARGS.debug:
        print(yaml.dump(_ptfdict, default_flow_style=False))
    return _ptfdict



def gen_fmid_sysmod_dict(global_csi,_ptfdict):
    """
    Generate FMIDs into Dictionary
    Dict Structure:
    CSI:
       ZONE:
           FMID:
                - SYSMOD1
                - SYSMOD2
    """
    if PARGS.debug:
        print('Start populating registry dictionary with FMIDs and SYSMODs')
    zone_name = ''
    sysmod_fmid = ''
    sysmod_name = ''
    sysmod_type = ''
    sysmod_status = ''
    sysmod_insdate = ''
    sysmod_feature = ''
    xline = 1
    yline = 50000
    gendict=False
    with open(PARGS.SMPEDATA_OUTPUT, 'r', encoding='cp1047') as smpein:
        for line in smpein:
            xline+=1
            if xline%yline == 0:
                PARGS.PROCIND+="".join('.')
                print(f'\r{PARGS.PROCIND}',end='')
            if line[10:24] == 'SYSMOD ENTRIES':
                zone_name = line[1:9].strip()
                continue
            if line[11:28] == 'FEATURE         =':
                sysmod_feature = line[29:120].strip()
            if line[11:28] == 'TYPE            =':
                sysmod_name = line[1:9].strip()
                sysmod_type = line[29:39].strip()
            if line[11:28] == 'STATUS          =':
                sysmod_status = line[29:49].strip()
            if line[11:18] == 'FMID   ' and sysmod_name != '' and 'GLOBAL' in zone_name:
                sysmod_fmid = line[29:39].strip()
                gendict=True
            if line[11:18] == 'FMID   ' and sysmod_name != '':
                sysmod_fmid = line[29:39].strip()
            if line[21:29] == 'REC   = ' and 'GLOBAL' in zone_name:
                sysmod_insdate = line[29:50].strip()
            if line[21:29] == 'INS   = ':
                sysmod_insdate = line[29:50].strip()
                gendict=True
            if gendict:
                gendict=False
                for dictcsi in _ptfdict.keys():
                    for dictzone in _ptfdict[dictcsi]:
                        if zone_name in dictzone and dictcsi == global_csi:
                            if sysmod_fmid not in _ptfdict[dictcsi][dictzone]:
                                _ptfdict[dictcsi][dictzone][sysmod_fmid] = {}
                            if sysmod_name not in _ptfdict[dictcsi][dictzone][sysmod_fmid]:
                                _ptfdict[dictcsi][dictzone][sysmod_fmid][sysmod_name] = {}
                            _ptfdict[dictcsi][dictzone][sysmod_fmid][sysmod_name]['Type'] = \
                                    sysmod_type
                            _ptfdict[dictcsi][dictzone][sysmod_fmid][sysmod_name]['Feature'] = \
                                    sysmod_feature
                            _ptfdict[dictcsi][dictzone][sysmod_fmid][sysmod_name]['Installed'] = \
                                    sysmod_insdate
                            _ptfdict[dictcsi][dictzone][sysmod_fmid][sysmod_name]['Status'] = \
                                    sysmod_status
                sysmod_feature = ''


    with open(PARGS.SMPESYSMDB, 'a', encoding='cp1047') as symdb:
        yaml.dump(_ptfdict, symdb, default_flow_style=False)

    return 




def regen_registry():
    """
    Regenerate the dictionary from smpe feature list report
    """
    print('..')
    if PARGS.debug:
        print('Begin generation of python dictionary')
    featdict={}
    featdict[PARGS.PRODREG] = {}
    feature = None
    chkmore=False
    pid = ''
    ver = ''
    with open(PARGS.SMPEDATA_OUTPUT, 'r', encoding='cp1047') as smpein:
        for lines in smpein.readlines():
            if lines[1:35] == '                                  ' or 'PAGE ' in lines[1:5]:
                continue
            if 'DESCRIPTION     =' in lines:
                feature = lines[1:9].rstrip()
                if feature not in featdict[PARGS.PRODREG]:
                    featdict[PARGS.PRODREG][feature] = {}
                featname = lines[29:120].rstrip()
                featdict[PARGS.PRODREG][feature]['name'] = featname
                chkmore=False
            if 'PRODUCT' in lines:
                pid = lines[29:38].rstrip()
                ver = lines[39:47].rstrip()
                featdict[PARGS.PRODREG][feature]['version'] = ver
                featdict[PARGS.PRODREG][feature]['pid'] = pid
            if 'FMID            =' in lines or chkmore:
                if chkmore and lines[29:30] == ' ':
                    continue
                if chkmore and lines[1:29] != '                            ':
                    continue
                fmidlist = lines[29:116].split(' ')
                for x in fmidlist:
                    if x != '':
                        if 'fmids' in featdict[PARGS.PRODREG][feature]:
                            featdict[PARGS.PRODREG][feature]['fmids'].append(x)
                        else:
                            featdict[PARGS.PRODREG][feature]['fmids'] = []
                            featdict[PARGS.PRODREG][feature]['fmids'].append(x)
                chkmore=True

    with open(PARGS.SMPEREGDB, 'w', encoding='cp1047') as yamlout:
        yaml.dump(featdict, yamlout, default_flow_style=False)
    if PARGS.debug:
        print('Initial registry dictionary structure build complete')


def print_prod_details(feature,reg_data):
    """
    Print all the FMIDS for specified feature
    """
    fmidstr = ''
    pfmd = 0
    product_reg = reg_data[PARGS.PRODREG]
    pr_red(f'{feature} Details')
    print('   Feature    Description                                              '\
            'PID        Version')
    print('  --------------------------------------------------------------------'\
            '--------------------')
    if feature in product_reg:
        pr_cyan(f"  {feature:9}" +\
              f"  {reg_data[PARGS.PRODREG][feature]['name']:55}" +\
              f"  {reg_data[PARGS.PRODREG][feature]['pid']:9}" +\
              f"  {reg_data[PARGS.PRODREG][feature]['version']:10}")
        pr_red(f'FMIDS for {feature}')
        for fmid in reg_data[PARGS.PRODREG][feature]['fmids']:
            fmidstr += str("".join(fmid)+" ")
            pfmd+=8
            if pfmd >= 80:
                fmidstr+='\n'
                pfmd = 0
        print(fmidstr)


def prod_summary(reg_data):
    """
    Print Feature Records
    """
    product_reg = reg_data[PARGS.PRODREG]
    print('   Feature    Description                                              '\
            'PID        Version')
    print('  --------------------------------------------------------------------'\
            '--------------------')
    for products in product_reg:
        pr_cyan(f"  {products:9}" +\
              f"  {reg_data[PARGS.PRODREG][products]['name']:55}" +\
              f"  {reg_data[PARGS.PRODREG][products]['pid']:9}" +\
              f"  {reg_data[PARGS.PRODREG][products]['version']:10}")


def run_rexx(smpetemp_yaml):
    """
    Run the rexx exec
    """

    _rexx_file = tempfile.NamedTemporaryFile(mode='w+b')
    _rexx_data_block = smpetemp_yaml['REXX']['DATA']
    with open(_rexx_file.name, 'w', encoding='cp1047') as rexxfile:
        for lines in _rexx_data_block.splitlines():
            lines = lines.ljust(79)
            rexxfile.write(lines+"\n")

    subprocess.run(['chmod', '750', _rexx_file.name],capture_output=False,check=True)
    subprocess.run([_rexx_file.name],capture_output=False, check=True)
    rexxfile.close()



def template_rexx(csiname,listcmd):
    """
    template rexx exec
    """
    PARGS.PROCIND += "".join('.')
    print(f'\r{PARGS.PROCIND}',end='')
    output_data = {"csiname": csiname,
                   "vardir": PARGS.SMPEREGDIR,
                   "smpout": PARGS.SMPOUT,
                   "smploga": PARGS.SMPLOGA,
                   "smplog": PARGS.SMPLOG,
                   "listcmd": listcmd,
                   "smpedata": PARGS.SMPEDATA_OUTPUT}

    with open(PARGS.SMPETEMPLATE_YAML, "r", encoding="cp1047") as template_file:
        template_data = template_file.read()

    # Create a Jinja environment and load the template
    env = jinja2.Environment(loader=jinja2.BaseLoader())
    template = env.from_string(template_data)

    # Update the template with new data
    output = template.render(output_data)
    return output

if __name__ == '__main__':
    PARGS = ''
    PARGS = parse_arguments()

    if not os.path.isdir(PARGS.SMPEREGDIR):
        os.mkdir(PARGS.SMPEREGDIR)

    if PARGS.summary:
        print(' ')
        loaded_smpereg_data = load_dict(PARGS.SMPEREGDB)
        loaded_custreg_data = load_dict(PARGS.CUSTREGDB)
        pr_red('SMPE Managed Registration Entries')
        prod_summary(loaded_smpereg_data)
        if loaded_custreg_data:
            print(' ')
            pr_red('Customer Registration Entries')
            prod_summary(loaded_custreg_data)
            print(' ')
    if PARGS.search:
        print(' ',flush=True)
        loaded_smpereg_data = load_dict(PARGS.SMPEREGDB)
        loaded_custreg_data = load_dict(PARGS.CUSTREGDB)
        pr_red('SMPE Managed Registration Entries')
        prod_search(loaded_smpereg_data,PARGS.search)
        if loaded_custreg_data:
            print(' ')
            pr_red('Customer Registration Entries')
            prod_search(loaded_custreg_data,PARGS.search)
            print(' ')
    if PARGS.add:
        if PARGS.input:
            update_data = load_dict(PARGS.input)
        else:
            update_data = False
        cust_add(update_data)
    if PARGS.fmidptfs:
        gen_fmidptfs_output(PARGS.fmidptfs)
    if PARGS.listzones:
        gen_zonelist_output(PARGS.listzones)
    if PARGS.zone:
        gen_sysmods_zone_output(PARGS.zone)
    if PARGS.sysmods:
        gen_sysmods_output(PARGS.sysmods)
    if PARGS.generate_template:
        subprocess.run(['rm', '-rf', PARGS.SMPOUT],capture_output=False,check=False)
        subprocess.run(['rm', '-rf', PARGS.SMPLOGA],capture_output=False,check=False)
        subprocess.run(['rm', '-rf', PARGS.SMPLOG],capture_output=False,check=False)
        subprocess.run(['rm', '-rf', PARGS.SMPEREGDB],capture_output=False,check=False)
        subprocess.run(['rm', '-rf', PARGS.SMPESYSMDB],capture_output=False,check=False)
        get_smpe_data('FEATURE')
        regen_registry()
        get_smpe_data('SYSMODS')
        pr_cyan('\nPython dictionary/registry build completed')
    if PARGS.feature:
        loaded_smpereg_data = load_dict(PARGS.SMPEREGDB)
        loaded_custreg_data = load_dict(PARGS.CUSTREGDB)
        print_prod_details(PARGS.feature,loaded_smpereg_data)
        if loaded_custreg_data:
            print_prod_details(PARGS.feature,loaded_custreg_data)
    print(' ')
    pr_cyan('End of processing')
    print(' ')
