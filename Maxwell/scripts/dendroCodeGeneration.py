# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:04:15 2018

@author: Dave

This is a script that reads in a csv file, containing variables for Dendro-GR
code, and then writes maxwellA.par.json, parameters.h, and parameters.cpp.
Hopefully it will also write utils files too.

!!! NOTES !!!

static const variables are defined and assigned in the parameters.h files. They never exist in the json file

extern variables are defined in the parameters.h, read in from the .json file, and assigned in parameters.cpp file
"""
import csv
import os

def main():
    print("Hello, World")
    
def createJson():
    #open our new .json file
    file = open("maxwellADAVE.par.json","w+")
    
    #start writing to the new .json file
    #writes everything EXCEPT the last '}'
    file.write("{")
    with open("DENDRO_GR_VAR_DATA.csv","r") as csvfile:
        
        reader = csv.reader(csvfile,delimiter=",")
        next(csvfile) #THIS SKIPS THE HEADER
        
        for row in reader:
            if (row[2] != "static const" and row[1] == "1"):
                file.write("\n\n\"" + row[4] +"\" : " + row[5] + ",")
            elif (row[2] != "static const" and row[1] != "1"):
                file.write("\n\n\"" + row[4] + "\" : [" + row[5] + "],")
    file.close()
    
    #This makes sure the last line does NOT end with a comma
    #which is a serious sin in a .json file
    with open('maxwellADAVE.par.json', 'rb+') as binaryFile:
        binaryFile.seek(-1, os.SEEK_END)
        binaryFile.truncate()
    
    #this adds opens the file in append mode and writes the final }
    file = open("maxwellADAVE.par.json","a")
    file.write("\n\n}")
    file.close()

def createHeader():
    file = open("parameters.h","w+")
    file.write("#ifndef SFCSORTBENCH_PARAMETERS_H\n")
    file.write("#define SFCSORTBENCH_PARAMETERS_H\n\n")
    file.write("#include <string.h>\n#include <iostream>\n\n\n")
    file.write("namespace maxwell\n{\n\n")
    
    file.write("\tstatic const unsigned int MAXWELL_ELE_ORDER = 4;\n\n")
    file.write("\tstatic const unsigned int MAXWELL_RK45_STAGES = 6;\n\n")
    file.write("\tstatic const unsigned int MAXWELL_RK4_STAGES = 4;\n\n")
    file.write("\tstatic const unsigned int MAXWELL_RK3_STAGES = 3;\n\n")
    file.write("\tstatic const double MAXWELL_SAFETY_FAC = 0.8;\n\n")
    
    #next four lines are NOT read in from JSON file. They are defined in parameters.cpp
    file.write("\textern unsigned int MAXWELL_TIME_STEP_OUTPUT_FREQ;")
    file.write("extern unsigned int MAXWELL_SPLIT_FIX;")
    file.write("\textern double MAXWELL_COMPD_MIN[3];\n\n\textern double MAXWELL_COMPD_MAX[3];\n\n")
    file.write("\textern double MAXWELL_OCTREE_MIN[3];\n\n\textern double MAXWELL_OCTREE_MAX[3];\n\n")
    
    
    with open("DENDRO_GR_VAR_DATA.csv","r") as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        next(csvfile) #THIS SKIPS THE HEADER
        
        
        for row in reader: 
            if (row[2] == "static const" and row[1] == "1"):
                file.write("\t" + row[2] + " " + row[3] + " " + row[4] + " = " + row[5] + ";\n\n")
            #I could add logic for static const and != 2 but its not applicable for now
            elif(row[2] == "extern" and row[1] == "1"):
                file.write("\t" + row[2] + " " + row[3] + " " + row[4] +";\n\n")
            elif(row[2] == "extern" and row[1] != "1"):
                file.write("\t" + row[2] + " " + row[3] + " " + row[4] + "[" + row[1] + "];\n\n")
            
                
        file.write("\tstatic const unsigned int MAXWELL_NUM_VARS_INTENL=(MAXWELL_RK45_STAGES+1)*MAXWELL_NUM_VARS;\n\n")
        file.write("}\n\n#endif //SFCSORTBENCH_PARAMETERS_H")
    

def createCpp():
    file = open("parameters.cpp","w+")
    
    file.write("#include \"parameters.h\"\n\n")
    file.write("namespace maxwell\n{\n\n")
    
    with open("DENDRO_GR_VAR_DATA.csv","r") as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        next(csvfile) #THIS SKIPS THE HEADER
        for row in reader:
            if (row[2] == "extern" and row[1] == "1"):
                file.write("\t" + row[3] + " " + row[4] + " = " +row[5] + ";\n\n")
            elif (row[2] == "extern" and row[1] != "1"):
                file.write("\t" + row[3] + " " + row[4] + "[" + row[1] + "] = {" + row[5] +"};\n\n")
                
    #Here, we assign values to the variables that do not exist in the .json
    file.write("\tdouble MAXWELL_COMPD_MIN[3]={MAXWELL_GRID_MIN_X,MAXWELL_GRID_MIN_Y,MAXWELL_GRID_MIN_Z};\n")
    file.write("\tdouble MAXWELL_COMPD_MAX[3]={MAXWELL_GRID_MAX_X,MAXWELL_GRID_MAX_Y,MAXWELL_GRID_MAX_Z};\n\n")
    file.write("\tdouble MAXWELL_OCTREE_MIN[3]={0.0,0.0,0.0};\n")
    file.write("\tdouble MAXWELL_OCTREE_MAX[3]={(double)(1u<<MAXWELL_MAXDEPTH),(double)(1u<<MAXWELL_MAXDEPTH),(double)(1u<<MAXWELL_MAXDEPTH)};\n\n")
    file.write("\tunsigned int MAXWELL_TIME_STEP_OUTPUT_FREQ=10;\n\n")
    file.write("\tunsigned int MAXWELL_SPLIT_FIX=2;\n\n")
    file.write("}")
    
#This function is still under construction!!!
def createReadParam():
    
    tab1 = "\t"
    tab2 = "\t\t"
    tab3 = "\t\t\t"
    line1 = "\n"
    line2 = "\n\n"
    nspace = "maxwell::"
    par = "par::Mpi_Bcast(&"
    
    file = open("readParam.cpp","w+")
    file.write("#include \"maxwellUtils.h\"\n\n")
    file.write("namespace maxwell\n{\n\n")
    file.write(tab1+"void readParamFile(const char * fName,MPI_Comm comm)\n" + tab1 + "{" + line2)
    file.write(tab2 + "json parFile;" + line1)
    file.write(tab2 + "int rank,npes;" + line1)
    file.write(tab2 + "MPI_Comm_rank(comm,&rank);" + line1)
    file.write(tab2 + "MPI_Comm_size(comm,&npes);" + line2)
    
    file.write(tab2 + "unsigned int vtu_len;" + line1)
    file.write(tab2 + "unsigned int chp_len;" + line1)
    file.write(tab2 + "unsigned int prf_len;" + line2)
    
    file.write(tab2 + "if(!rank)" + line1 + tab2 + "{" + line1)   
    file.write(tab3 + "std::ifstream infile(fName);" + line1)
    file.write(tab3 + "if(!infile) {std::cout<<fName<<\" parameter file open failed \"<<std::endl;}" + line1)
    file.write(tab3 + "infile>>parFile;" + line2)
    
    with open("DENDRO_GR_VAR_DATA.csv","r") as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        next(csvfile) #THIS SKIPS THE HEADER
        for row in reader:
            if(row[2] == "extern"):
                file.write(tab3 + nspace + row[4] + "=parFile[\"" + row[4] + "\"];" + line1)
    
    file.write(line1)
    
    #This is probably defined above in the for loop.
    #I will need to delete the early def/assign
    file.write(tab3 + "for(unsigned int i=0;i<maxwell::MAXWELL_NUM_REFINE_VARS;i++)" + line1)
    file.write(tab3 + tab1 + "maxwell::MAXWELL_REFINE_VARIABLE_INDICES[i]=parFile[\"MAXWELL_REFINE_VARIABLE_INDICES\"][i];" + line2)
    file.write(tab3 + "for(unsigned int i=0;i<maxwell::MAXWELL_NUM_EVOL_VARS_VTU_OUTPUT;i++)" + line1)
    file.write(tab3 + tab1 + "maxwell::MAXWELL_VTU_OUTPUT_EVOL_INDICES[i]=parFile[\"MAXWELL_VTU_OUTPUT_EVOL_INDICES\"][i];" + line2)
    
    file.write(tab3 + "vtu_len=MAXWELL_VTU_FILE_PREFIX.size();" + line1)
    file.write(tab3 + "chp_len=MAXWELL_CHKPT_FILE_PREFIX.size();" + line1)
    file.write(tab3 + "prf_len=MAXWELL_PROFILE_FILE_PREFIX.size();" + line2 + tab2 +"}" + line2 + line1)
    
    with open("DENDRO_GR_VAR_DATA.csv","r") as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        next(csvfile) #THIS SKIPS THE HEADER
        for row in reader:
            if(row[2] == "extern"):
                file.write(tab2 + par + row[4] + ",1,0,comm);" + line1)
    file.write(line2)
    #This writes lines 120-149
    #Which I believe should be hard coded
    #I added brackets around the for loops for safety.
    #I did not add brackets to C++ for loops for safety,
    #but I think it would be a good idea
    file.write(tab2 + "if(!rank)" + line1 + tab2 + "{" + line1)
    file.write(tab3 + "for(unsigned int k=0;k<vtu_len;k++){" +line1)
    file.write(tab3 + tab1 + "vtu_name[k]=MAXWELL_VTU_FILE_PREFIX[k];" +line1 + tab3 + "}" + line2)
    file.write(tab3 + "for(unsigned int k=0;k<chp_len;k++){" + line1)
    file.write(tab3 + tab1 + "chp_name[k]=MAXWELL_CHKPT_FILE_PREFIX[k];" + line1 + tab3 + "}" +line2)
    file.write(tab3 + "for(unsigned int k=0;k<prf_len;k++){" + line1)
    file.write(tab3 + tab1 + "prf_name[k]=MAXWELL_PROFILE_FILE_PREFIX[k];" + line1 + tab3 + "}" +line2)
    file.write(tab3 + "vtu_name[vtu_len]='\\0';" + line1)
    file.write(tab3 + "chp_name[chp_len]='\\0';" + line1)
    file.write(tab3 + "prf_name[prf_len]='\\0';" + line2)
    file.write(tab2 + "}" + line2)
    file.write(tab2 + "MPI_Bcast(vtu_name,vtu_len+1,MPI_CHAR,0,comm);" + line1)
    file.write(tab2 + "MPI_Bcast(chp_name,chp_len+1,MPI_CHAR,0,comm);" + line1)
    file.write(tab2 + "MPI_Bcast(prf_name,prf_len+1,MPI_CHAR,0,comm);" + line2)
    file.write(tab2 + "MAXWELL_VTU_FILE_PREFIX=std::string(vtu_name);" + line1)
    file.write(tab2 + "MAXWELL_CHKPT_FILE_PREFIX=std::string(chp_name);" + line1)
    file.write(tab2 + "MAXWELL_PROFILE_FILE_PREFIX=std::string(prf_name);" + line2) 
    """
    END lines 120-149, also the brackets might
    not be so necessary if no one needs to edit
    the autogenerated files
    """
    
    
    
#createReadParam()    
createCpp()
createJson()
createHeader()
