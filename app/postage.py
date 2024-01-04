import os
import datetime

#Getting the path of the current logseq journal
def getTodayJournalPath(graph_path) :
    journal_path = ''
    today = str(datetime.date.today())
    today_journal = today.replace("-","_") + '.md'
    
    try :
        if'journals' in os.listdir(graph_path) :
            if graph_path[-1]!='/' :
                journal_path = graph_path+'/journals/'
            else :
                journal_path = graph_path+'journals/'

            return journal_path + today_journal
    except Exception as e :
        print ("Journal folder not found in specified graph")

#Inserting a message in today's journal
def newBlock(path,inbox) :
    print ("path : ",path)
    print ("message : ",inbox)
    try :
        with open(path,'a') as f : 
            f.write("\n- "+inbox)
        print ('success')
    except Exception as e :
        print("error in the writing")