/subit/expense/
POST, returns a json
input: date (optional), text, amount, token
output: status:ok

/subit/income/
POST, returns a json
input: date (optional), text, amount, token
output: status:ok

/accounts/register/
step1:
  POST
  input: username. email, password
  output: status:ok
step2: #click on link with the code in the email
  GET
  input: email, code
  output: status: ok (shows the token)
/q/generalstat/
  POST, returns a json
  input: fromdate (optional), todate(optional), token
  output: json from ssome general stats related to this user
