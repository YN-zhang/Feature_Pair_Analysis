import sys
import pandas as pd



ref=pd.read_csv("mGAM_feature_01.csv")
columns=list(ref.columns)
columns.remove('name')
title="Window_Pair"
output_file=sys.argv[1]
dict1 = {}

for i in range(len(columns)):
#	first_TF=columns[i]
	first_TF = columns[i]
	for j in range(i+1):
		second_TF=columns[j]
		chip=first_TF+'_'+second_TF
		title=title+','+chip
output=open(output_file.strip('list')+"feature_pair.csv",'w')
output.write(title+"\n")
with open(sys.argv[1]) as input_f:
	content=input_f.readlines()

occur=0
temp_df=ref.set_index('name')
dict1=temp_df.to_dict()
for line in content:
	temp1=line.strip('\n')
	temp=temp1.split('\t')
	window1=temp[0]
	window2=temp[1]
	output_list=[]
	output_line=temp[0]+"&"+temp[1]
	result=[]
	for i in range(len(columns)):
        	first_TF=columns[i]
        	for j in range(i+1):
                    second_TF=columns[j]
                    ####case 1
                    w1_TF1=dict1[first_TF][window1]
                    w2_TF2=dict1[second_TF][window2]
                    res1=min(w1_TF1,w2_TF2)

		    #### case 2
                    w1_TF2=dict1[second_TF][window1]
                    w2_TF1=dict1[first_TF][window2]
                    res2=min(w1_TF2,w2_TF1)
                    min_res=min(res1,res2)
                    max_res=max(res1,res2)
                    occur= max_res
                    output_line=output_line+','+str(max_res)
                    occur=0
	output.write(output_line+'\n')
output.close()
