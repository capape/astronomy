#!/bin/bash

function split_name {

    if [ "${LABEL}" = "Supernova" ]
    then
        echo "${1}"
        return
    fi
    
    current_ifs=${IFS}
    IFS='_'
    read -ra strarr <<< "${1}"


    for val in "${strarr[@]}";
    do
        echo "${val}"
    done    

    IFS=${current_ifs}
    
}

function objectData {
    PREFIX="${2}"
    LABEL="${3}"
    for objectFile in $(find ${1} -type f -name "${PREFIX}*PROCESSED.fit");
    do
        DATE_OBS=$(fitsheader ${objectFile}  | grep DATE-OBS | sed -s "s/DATE-OBS=//" | sed -s "s/\/\sUT\s*//" | sed -s "s/ \/ Y.*//")
        FILE_NAME=$(basename ${objectFile})
        OBJECT_NAME=$(echo ${FILE_NAME} | sed -s "s/${PREFIX}_//" | sed -s "s/_PROCESSED.fit//")
        for obj in $(split_name "${OBJECT_NAME}" "${LABEL}"); do 
            echo "${LABEL}: ${obj}, Date: ${DATE_OBS} "
        done
    done | sort
} 

function galaxyData {
    objectData "${1}" "GLX_DS" Galaxy
}

function supernovaData {
    objectData "${1}" "GSN_R" Supernova
}

function cluster {
    objectData "${1}" "CG_DS" "Cluster"
    objectData "${1}" "CO_DS" "Cluster"
}

function nebulae {
    objectData "${1}" "NP_DS" "Nebulae"  
    objectData "${1}" "NPN_DS" "Nebulae"  
}

function quasar {
    objectData "${1}" "QUASAR_DS" "Quasar"      
}

function countDistinctObject {
    object="${1}"
    file_data="${2}"
    
    count=$(grep "${object}" "${file_data}" | cut -f1 -d',' | cut -f2 -d':' | sort -u | wc -l )
    echo "${object} : ${count}"

}

function countObject {
    object="${1}"
    file_data="${2}"
    
    count=$(grep "${object}" "${file_data}" | cut -f1 -d',' | cut -f2 -d':' | wc -l )
    echo "${object} : ${count}"

}

{
    galaxyData ${1} 
    supernovaData ${1}
    cluster ${1}
    nebulae ${1}
    quasar ${1}
} > tmp-data.txt

function getWeek {
     date --date="${1}" +"%Y-week-%W"
}

function observationWeeks {
    for observation_date in  $(cat ${1}  | cut -f2 -d',' | sed -e 's/.*Date\: *//' | sed -e "s/'//g"); do
        getWeek "${observation_date}"
    done | sort -u | wc -l
}


numberOfDaysObserving=$(observationWeeks tmp-data.txt)
echo "Observation days: ${numberOfDaysObserving}"

{
countObject Galaxy tmp-data.txt
countObject Supernova tmp-data.txt
countObject Nebulae tmp-data.txt
countObject Quasar tmp-data.txt
countObject Cluster tmp-data.txt
} | awk 'BEGIN{FS=":";total=0;printf("------------------\n");printf("Total observations\n");printf("------------------\n");}{printf("%-12s: %4d\n",$1,$2);total+=$2}END{printf("------------------\n");printf("%-12s: %4d\n","Total", total)}'

{
countDistinctObject Galaxy tmp-data.txt
countDistinctObject Supernova tmp-data.txt
countDistinctObject Nebulae tmp-data.txt
countDistinctObject Quasar tmp-data.txt
countDistinctObject Cluster tmp-data.txt
} | awk 'BEGIN{FS=":";total=0;printf("------------------\n");printf("Total objects\n");printf("------------------\n");}{printf("%-12s: %4d\n",$1,$2);total+=$2}END{printf("------------------\n");printf("%-12s: %4d\n","Total", total)}'




cat tmp-data.txt | sort -k 4
rm tmp-data.txt