import sys
import os


if len(sys.argv) != 4:
    print('Incorrect number of arguments!')
    exit()

input_filename = sys.argv[1]
occupations_output_filename = sys.argv[2]
states_output_filename = sys.argv[3]
if not os.path.isfile(input_filename):
    print("File {} does not exist.".format(input_filename))
    exit()

#for this project we only need three columns CASE_STATUS, SOC_NAME, WORKSITE_STATE. we'll get these three columns index from the data
def get_columns_index(headers):
    CASE_STATUS_index = -1
    SOC_NAME_index = -1
    WORKSITE_STATE_index = -1

    for i in range(len(headers)):
        column_name = headers[i].upper()
        #file field name is called CASE_STATUS or 'STATUS'
        if column_name == 'CASE_STATUS' or column_name == 'STATUS': 
            CASE_STATUS_index =i
        #file field name is called SOC_NAME or 'LCA_CASE_SOC_NAME'
        elif column_name == 'SOC_NAME' or column_name == 'LCA_CASE_SOC_NAME': 
            SOC_NAME_index = i
        #file field name is called WORKSITE_STATE or 'LCA_CASE_WORKLOC1_STATE'
        elif column_name == 'WORKSITE_STATE'or column_name == 'LCA_CASE_WORKLOC1_STATE': 
            WORKSITE_STATE_index = i
    #check if three columns CASE_STATUS, SOC_NAME, WORKSITE_STATE exist in the file
    if CASE_STATUS_index == -1 or SOC_NAME_index == -1 or WORKSITE_STATE_index == -1:
       print("Please check if three columns CASE_STATUS, SOC_NAME, WORKSITE_STATE exist in the file {}".format(input_filename))
       exit() 
    return CASE_STATUS_index, SOC_NAME_index, WORKSITE_STATE_index

# Do processing while reading the file, one line at a time (This would account for huge files and limited memory),read the file data into dictionary ({key: value}
def items_cnt(f): 
    total_certified = 0
    occupation_cnt = {}
    state_cnt = {}
    for line in f: 
        line = line.strip()
        if len(line) > 0:
            data_line = line.split(";")        
            case_status = data_line[CASE_STATUS_index].strip('\"').strip().upper()
            if case_status =='CERTIFIED':
                total_certified += 1
            
                occupation_name = data_line[SOC_NAME_index].strip('\"').strip().upper()
                state_name = data_line[WORKSITE_STATE_index].strip('\"').strip().upper()
                if occupation_name: #Do not count empty data
                    if occupation_name in occupation_cnt:
                        occupation_cnt[occupation_name] += 1
                    else:
                        occupation_cnt[occupation_name] = 1
                if state_name: #Do not count empty data
                    if state_name in state_cnt:
                        state_cnt[state_name] += 1
                    else:
                        state_cnt[state_name] = 1

    return occupation_cnt,state_cnt,total_certified

def get_top10_items(items_cnt):
    items = [(item,cnt,round(cnt/total_certified*100,1)) for item,cnt in items_cnt.items()]
    return sorted(items, key=lambda kv:(-kv[1], kv[0]))[:10]

# Write the top_items results to the file
def write_results_to_files(top_items, fieldnames,output_filename):
    with open(output_filename, "w") as out_file:
        out_file.write(';'.join('%s' % name for name in fieldnames))
        out_file.write('\n')
        out_file.write('\n'.join('%s;%s;%s%%' % item for item in top_items))
       

with open(input_filename, "r") as f:
    #deal with edge cases, file has empty lines in front of header or in the middle of the file. 
    while True:
        line = f.readline()
        if line is None: #end of file
            print("No data in the file {}".format(input_filename))
            exit()

        line = line.strip()
        if len(line) > 0:
            headers = line.split(";")
            if len(headers) == 0:
                print("No data in the file {}".format(input_filename))
                exit()
            break

    #get three columns CASE_STATUS, SOC_NAME, WORKSITE_STATE index in the file
    CASE_STATUS_index, SOC_NAME_index, WORKSITE_STATE_index = get_columns_index(headers)
        
    occupation_cnt,state_cnt,total_certified = items_cnt(f)
    
    top_occupations = get_top10_items(occupation_cnt)
    top_states = get_top10_items(state_cnt)
    fieldnames = ["TOP_OCCUPATIONS","NUMBER_CERTIFIED_APPLICATIONS","PERCENTAGE"]
    write_results_to_files(top_occupations, fieldnames,occupations_output_filename)
    #change to top_10_states.txt file field name which only the first field name is different. 
    fieldnames[0] = 'TOP_STATES'
    write_results_to_files(top_states, fieldnames,states_output_filename)

        
  