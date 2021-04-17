# restful_cosmo_db

Before using change endpoint and key values in config.ini file.

The db can contain students and their grades. Main and mandatory fields are last_name and grade, other are fields are optional.
At first db is empty.

  <h3>cosmos db database connection</h3></br>
    <p>
    - <a href="/restart">/restart</a> -> to restart database</br>
    - <a href="/get">/get</a> -> to get all queries</br>
    - <a href="/add">/add</a>?last_name=(user_last_name)&grade=(int_mark_for_student) [&first_name=(user_first_name)] -> add new student grade</br>
    - <a href="/get">/get</a>?last_name=(user_last_name) [&first_name=(user_first_name)] -> get all user grades</br>
    - <a href="/get_mean">/get_mean</a>?last_name=(user_last_name) [&first_name=(user_first_name)] -> get mean user grade</br>
    </p>
    
   
