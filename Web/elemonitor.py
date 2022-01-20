from flask import Flask,render_template,redirect,flash,session,request,session, json
import os
from datetime import datetime

from tb import tb_auth_controller
from tb import tb_device_controller
from tb import tb_telemetry_controller
from tb import tb_rpc_controller

app = Flask(__name__,template_folder='templates')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app.secret_key = 'flashai'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def root():
    if 'loggedin' in session:
        return redirect('/dashboard')
    else:
        return render_template('auth-signin.html')


@app.template_filter('strfdelta')
def strfdelta(s):
    delta = datetime.now().timestamp()-int(s/1000)
    return int(delta/60)

@app.template_filter('lengthArr')
def lengthArr(arr):
    return len(arr)

@app.template_filter('ctime')
def timectime(s):
    return datetime.fromtimestamp(int(s/1000))

@app.route('/signin',methods=['POST','GET'])
def authenticate():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            result = tb_auth_controller.tb_login(username,password)

            if result.status_code ==200:
                print("sign-in success")
                session['loggedin'] = True
                session['username'] = username
                session['token'] = result.json()['token']

                result1 = tb_auth_controller.tb_getUser(result.json()['token'])
                # print(result1.json())
                if result1.status_code ==200:
                    print('Store Session')
                    session['tenantId_entityType'] = result1.json()['tenantId']['entityType']
                    session['tenantId_id'] = result1.json()['tenantId']['id']
                    session['customer_id'] =  result1.json()['customerId']['id']
                    session['authority'] = result1.json()['authority']
                    print('----------------')
                    
                    # return render_template('dashboard.html')

                    return redirect('/dashboard')
                else:
                    return render_template('auth-signin.html')

            else:
                return render_template('auth-signin.html')
            
        else:
            flash('Invalid Username or Password !!')
            print("wrong pass")
            return render_template('auth-signin.html')
    except Exception as e:
        print('Error Authentication' + e)


@app.route('/signup', methods=['POST'])
def register():
    return render_template('auth-signup.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.clear()
    return render_template("auth-signin.html")


@app.route('/dashboard')
def dashboard():
    
    if 'loggedin' in session:
        print('dashboard')

    # if  session['loggedin']:
        # print(session['authority'])
        if session['authority'] == "TENANT_ADMIN":
            print('authority = TENANT_ADMIN')

            devices = tb_device_controller.tb_getTenantDeviceInfos(session['token'], 0, 30)
            if devices.status_code != 200:
                return render_template('auth-signin.html')
            
            #print(json.dumps(devices.json(), indent=4))
            
            device_attribute= {'data':[]}
            for device in devices.json()['data']:
                attribute = tb_telemetry_controller.tb_getAttributesByScope(session['token'], 'DEVICE', device['id']['id'],'lastActivityTime')
                if attribute.status_code != 200:
                    return render_template('auth-signin.html')

                device_attribute['data'].append({'device_detail':device,'device_attribute':attribute.json()})

            print(json.dumps(device_attribute['data'], indent=4))
            
            return render_template('dashboard.html',devices = devices.json(),device_attribute=device_attribute)
            
        else:
            
            devices = tb_device_controller.tb_getCustomerDevices(session['token'],session['customer_id'], 0, 30)

            if devices.status_code != 200:
                return render_template('auth-signin.html')

            device_attribute= {'data':[]}
            for device in devices.json()['data']:
                attribute = tb_telemetry_controller.tb_getAttributesByScope(session['token'], 'DEVICE', device['id']['id'],'lastActivityTime')
                if attribute.status_code != 200:
                    return render_template('auth-signin.html')
                device_attribute['data'].append({'device_detail':device,'device_attribute':attribute.json()})

            return render_template('dashboard.html',devices = devices.json(),device_attribute=device_attribute)
            
    else:
        return render_template('auth-signin.html')

@app.route('/attribute/<device_id>', methods=['POST', 'GET'])
def attribute(device_id):
    if 'loggedin' in session:

        if request.method == 'POST':
            voltages = tb_device_controller.tb_getTimeseries(session['token'],device_id, "voltage", 1000*60*60)
            currents = tb_device_controller.tb_getTimeseries(session['token'],device_id, "current", 1000*60*30)
            energy = tb_device_controller.tb_getTimeseries(session['token'],device_id, "total energy", 1000*60)
            return  app.response_class(
                json.dumps({"voltage": voltages.json(), "current": currents.json(), "energy": energy.json()}),
                status=200,
                mimetype='application/json'
            )

        voltages = tb_device_controller.tb_getTimeseries(session['token'],device_id, "voltage", 1000*60*60)
        currents = tb_device_controller.tb_getTimeseries(session['token'],device_id, "current", 1000*60*30)
        energy = tb_device_controller.tb_getTimeseries(session['token'],device_id, "total energy", 1000*60)

        info = tb_device_controller.tb_getDeviceInfoById(session['token'],device_id)
        if info.status_code != 200:
            return render_template('auth-signin.html')

        result = tb_device_controller.tb_get_timeseries_device_last_telemetry(session['token'],device_id, "voltage,current,total energy")

        if result.status_code == 200:
            return render_template('attribute.html',telemetry = result.json(), device_info = info.json(), voltages = voltages.json(), currents = currents.json(), energy = energy.json(), device_id=device_id, token = session['token'])
        else:
            return render_template('auth-signin.html')
    else:
        return render_template('auth-signin.html')


@app.route('/profile')
def profile():
    result =  tb_auth_controller.tb_getUser(session['token'])
    if result.status_code ==200:
        return render_template('profile.html',user = result.json(),error = "")
    else:
        return render_template('auth-signin.html')

@app.route('/changePassword',methods=['POST'])
def change_password():
    if 'loggedin' in session:
        pw =  str(request.form['pw'])
        newpw1 = str(request.form['newpw1'])
        newpw2 = str(request.form['newpw2'])

        result =  tb_auth_controller.tb_getUser(session['token'])
        if result.status_code !=200:
                return render_template('auth-signin.html')

        if newpw1!= newpw2:
            return render_template('profile.html',user = result.json(),error="Mật khẩu không đúng")
        else:
            change_pass_status = tb_auth_controller.tb_changePassword(session['token'], pw, newpw1)
            if change_pass_status.status_code !=200:
                return render_template('profile.html',user = result.json(),error="Sai Mật khẩu")
            else:
                return render_template('profile.html',user = result.json(),error="Đổi Mật khẩu Thành Công")
    else:
        return render_template('auth-signin.html')


response_out_ok = app.response_class(
            json.dumps({'result':'successfull'}),
            status=200,
            mimetype='application/json'
            )

response_out_nok = app.response_class(
            json.dumps({'result':'unsuccessfull'}),
            status=200,
            mimetype='application/json'
)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port="5098")