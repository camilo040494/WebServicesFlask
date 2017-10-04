#!/usr/bin/python
#
# El siguiente programa permite obtener algunos valores de un sistema operativo
# Linux (algunas cosas funcionan en Mac) pero que se accede a la informacion a
# traves de Web Services.
 
# Librerias que se requieren para correr la aplicacion
from flask import Flask, jsonify, make_response, request
import subprocess
 
# Se crea un objeto de tipo Flask llamado 'app'
app = Flask(__name__)
 
#
#
@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
        #
        # Almacene en la variable 'output' un mensaje que describa todos los 
        # web services definidos aqui
        #
        output = "Presentado por: Hassan Taleb y Camilo Pimienta"
        return output
#
# 'VBoxManage list ostypes'
# curl -i http://localhost:5000/vms/ostypes
#
@app.route('/vms/ostypes',methods = ['GET'])
def ostypes():
        ostypes = subprocess.Popen(['VBoxManage', 'list', 'ostypes'], stdout = subprocess.PIPE)
        output = subprocess.check_output(['cut', '-d', '\n', '-f', '8-'], stdin = ostypes.stdout)
        return jsonify({'vms': output})
#
#
# 'VBoxManage list vms'
# curl -i http://localhost:5000/vms
#
@app.route('/vms',methods = ['GET'])
def listvms():
        vms = subprocess.Popen(['VBoxManage', 'list', 'vms'], stdout = subprocess.PIPE)
        output = subprocess.check_output(['cut', '-d', '\n', '-f', '8-'], stdin = vms.stdout)
        if len(output) <= 1:
            output = "There are no machines created"
        return jsonify({'vms': output})
#
# 'VBoxManage list runningvms'
# curl -i http://localhost:5000/vms/running
#
@app.route('/vms/running', methods = ['GET'])
def running():
        running = subprocess.Popen(['VBoxManage', 'list', 'runningvms'], stdout = subprocess.PIPE)
        output = subprocess.check_output(['cut', '-d', '\n', '-f', '8-'], stdin = running.stdout)
        if len(output) <= 1:
            output = "There are no machines running"
        return jsonify({'vms': output})
#
# VBoxManage showvminfo default
# curl -i http://localhost:5000/vms/info/<string:vmname>
#
@app.route('/vms/info/<string:vmname>',methods=['GET'])
def infovmname(vmname):
        info = subprocess.Popen(['VBoxManage', 'showvminfo', vmname], stdout = subprocess.PIPE)
        output = subprocess.check_output(['cut', '-d', '\n', '-f', '8-'], stdin = info.stdout)
        return jsonify({'vms': output})

#
# VBoxManage create vm
# curl -i -H "Content-Type: application/json" -X POST -d '{ "name": "os-web", "cpu": "4", "ram": "580" }' http://localhost:5000/vms
#
@app.route('/vms',methods = ['POST'])
def createvm():
        if not request.json or not 'name' in request.json:
            abort(400)
        name = request.json['name']
        cpu = request.json.get('cpu', "1")
        ram = request.json.get('ram', "512")
        hdd = request.json.get('hdd', "5000")
        vdi = "/virtualbox/vms/"+name+".vdi"
        satacontroleler = "SATA Controller"

        vms = subprocess.Popen(['VBoxManage', 'createvm', '--name', name, '--register'], stdout = subprocess.PIPE)
        subprocess.check_output(['VBoxManage', 'modifyvm', name, '--memory', ram])
        #subprocess.check_output(['VBoxManage', 'modifyvm', name, '--memory', ram, '--acpi', 'on', '--boot1', 'dvd', '--nic1', 'nat'])
        subprocess.check_output(['VBoxManage', 'createvdi', '--filename', vdi, '--size', hdd])
        subprocess.check_output(['VBoxManage', 'modifyvm', name, '--ostype', 'RedHat_64'])
        subprocess.check_output(['VBoxManage', 'modifyvm', name, '--cpus', cpu])
        subprocess.check_output(['VBoxManage', 'storagectl', name, '--name', satacontroleler, '--add', 'sata'])
        subprocess.check_output(['VBoxManage', 'storageattach', name, '--storagectl', satacontroleler, '--port', '0', '--device', '0', '--type', 'hdd', '--medium', vdi])
        subprocess.check_output(['VBoxManage', 'storageattach', name, '--storagectl', satacontroleler, '--port', '1', '--device', '0', '--type', 'dvddrive', '--medium', 'emptydrive'])
        output = subprocess.check_output(['cut', '-d', '\n', '-f', '8-'], stdin = vms.stdout)
        return jsonify({'vm': output})


#
# VBoxManage delete vm
# curl -i -X DELETE http://localhost:5000/vms/<string:vmname> 
#
@app.route('/vms/<string:vmname>', methods=['DELETE'])
def deletevm(vmname):
        if len(vmname) == 0:
            abort(404)
        delete = subprocess.Popen(['VBoxManage', 'unregistervm', vmname, '--delete'], stdout = subprocess.PIPE)
        output = subprocess.check_output(['cut', '-d', '\n', '-f', '8-'], stdin = delete.stdout)
        return "Maquina borrada satisfactoriamente \n"


#
# Este es el punto donde arranca la ejecucion del programa
#
if __name__ == '__main__':
        app.run(debug = True, host='0.0.0.0')
 