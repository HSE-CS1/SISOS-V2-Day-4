from flask import Flask, render_template, request, redirect, flash
import queries as q
import os

app = Flask(__name__)
app.secret_key = os.getenv("MSG_KEY")

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/all")
def all():
  rows = q.get_all_passes()
  # rows will be a LIST of DICT items
  # each DICT will be one row from our databse
  # the keys of the DICT will be the column names from the table
  return render_template("all.html", rows=rows)

@app.route("/today")
def today():
  today = q.get_today().get("c_date")
  rows = q.get_todays_passes(today)
  return render_template("day.html", rows=rows, day=today)
  # make a template page for this route that shows a table of the 
  # returned data, but only show the first and last name,
  # location and times (in and out) in order by out_time

@app.route("/summary")
def summary():
  # this route should show number of passes per student
  rows = q.get_summary()
  return render_template("summary.html", rows=rows)

@app.route("/summary/<string:stu_id>")
def stu_summary(stu_id):
  student_name = q.get_student_name(stu_id)
  rows = q.get_stu_summary(stu_id)
  return render_template("stu_summary.html", rows=rows, student_name=student_name)

@app.route("/summary/<string:stu_id>/<string:loc>")
def stu_loc_summary(stu_id, loc):
  student_name = q.get_student_name(stu_id)
  rows = q.get_stu_loc_summary(stu_id, loc)
  return render_template("stu_loc_summary.html", 
                         location=loc,
                         student=student_name,
                         rows=rows,
                         stu_id=stu_id)
  
@app.route("/student", methods=["GET","POST"])
def student():
  if request.method == "GET":
    rows = q.get_all_students()
    return render_template("stu_form.html", rows=rows)
  else:
    stu_id = request.form.get("s_id")
    return redirect(f"/summary/{stu_id}")

@app.route("/signin", methods=["GET", "POST"])
def signin():
  if request.method == "GET": # clicked the link
    # show a form for the student to type in their student id
    return render_template("signinform.html")
  else: # PROCESS THE FORM
    stu_id = request.form.get("stu_id").upper()
    pass_id = q.check_for_pass(stu_id)
    #check for errors
    if pass_id == 0:
      flash(f"Sorry, No passes found for Student {stu_id}")
      return redirect("/signin")
    elif pass_id == -1:
      flash("ERROR - PLEASE SEE MR. FISHEL!!!!!")
      return redirect("/")
    else: # only one pass matched
      # update the passes table with the current time
      result = q.sign_back_in(pass_id)
      if result == 1:
        stu_name = q.get_student_name(stu_id)
        flash(f"Student {stu_id}, {stu_name} is now signed back into class.")
        return redirect("/all")
      else:
        return "ERROR - Please contact the system adminstrator!!!"

@app.route("/signout", methods=["GET","POST"])
def signout():
  if request.method == "GET":
    # show the form for the student to fill out
    return render_template("signoutform.html")
  else:
    # process the form
    # collect the data from the form
    pass_data = {
      "stu_id" : request.form.get("stu_id").upper(),
      "first" : request.form.get("first").title(),
      "last" : request.form.get("last").title(),
      "loc" : request.form.get("loc"),
      # date and time will come from our get_today function
      "pass_date" : q.get_today().get("c_date"),
      "out_time" : q.get_today().get("c_time")
    }
    # run the SQL to insert a row to the database
    pass_id = q.insert_pass(pass_data)
    flash(f"Pass # {pass_id} for {pass_data.get('first')} was created!!!")
    return redirect("/all")
    # return f"Pass # {pass_id} was created successfully!"
  











if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)