import os
import ast
def get_all_PLS_logs():
    dirname = os.path.dirname(__file__)
    allLogs=[]
    for file_name in os.listdir(dirname+"/logs"):
        if file_name.endswith(".txt"):
            file_elems=file_name.split("_")
            if(file_elems[0]=="PLS1" or file_elems[0]=="PLS2"):
                # file_characteristic={
                #     "PLS_type":file_elems[0],
                #     "n":int(file_elems[2]),
                #     "p":int(file_elems[4]),
                # }
                log={}
                log_file_path=os.path.join(dirname+"/logs", file_name)
                with open(log_file_path) as PLS_log:
                    line=PLS_log.readline()
                    while line:
                        if(line=="logType"):
                            logType=PLS_log.readline()
                            log["logType"]=logType
                            PLS_log.readline()
                            continue
                        if(line=="non_domines_approx"):
                            non_domines_approx=ast.literal_eval(PLS_log.readline())
                            log["non_domines_approx"]=non_domines_approx
                            PLS_log.readline()
                            continue
                        if(line=="fonction de voisinage"):
                            fonction_de_voisinage=PLS_log.readline()
                            log["fonction_de_voisinage"]=fonction_de_voisinage
                            PLS_log.readline()
                            continue
                        if(line=="objets"):
                            objets=ast.literal_eval(PLS_log.readline())
                            log["objets"]=objets
                            PLS_log.readline()
                            continue
                        if(line=="capacité max"):
                            W=int(float(PLS_log.readline()))
                            log["W"]=W
                            PLS_log.readline()
                            continue
                        if(line=="execution_time"):
                            execution_time=float(PLS_log.readline())
                            log["execution_time"]=execution_time
                            PLS_log.readline()
                            continue
                        if(line=="n"):
                            n=int(float(PLS_log.readline()))
                            log["n"]=n
                            PLS_log.readline()
                            continue
                        if(line=="p"):
                            p=int(float(PLS_log.readline()))
                            log["p"]=p
                            PLS_log.readline()
                            continue
                allLogs.append(log)
    return allLogs

