
function main(){
    $start = 0
    $finish = 777
    for ($i=$start; $i -lt $finish; $i++){
        $val = "{0:D6}" -f $i
        echo $val  
        python multiview_script.py --raw_dataset_dir './SoftRasDataset/' --mesh_number $val
    }
}

main
