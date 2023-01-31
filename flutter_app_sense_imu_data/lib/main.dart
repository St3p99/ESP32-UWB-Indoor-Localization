import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'package:sensors_plus/sensors_plus.dart';

import 'models/data.dart';

void main() => runApp(const MyApp());

class MyApp extends StatefulWidget {
  const MyApp({Key key}) : super(key: key);

  @override
  // ignore: library_private_types_in_public_api
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  //APP PARAMETERS
  bool _start = false;
  AccelerometerEvent _aevent;
  GyroscopeEvent _gevent;
  MagnetometerEvent _mevent;
  StreamSubscription accelerometerSubscription;
  StreamSubscription gyroscopeSubscription;
  StreamSubscription magnetometerSubscription;
  int _selectedChip = -1;
  Timer _timer;
  Data _imuData;
  bool _connected = false;

  //MQTT PARAMETERS
  final String _address = "D:00:22:EA:82:60:3B:9B";
  final String _brokerHost = "192.168.1.53";
  final String _port = "1883";
  MqttServerClient client;
  String topic1 = 'IMU_DATA'; // Not a wildcard topic

  @override
  void initState() {
    super.initState();
    client = MqttServerClient(_brokerHost, _port);

    /// Set the correct MQTT protocol for mosquito
    client.setProtocolV311();
    client.logging(on: false);
    client.keepAlivePeriod = 20;

    client.onConnected = onConnected;
    client.onDisconnected = onDisconnected;
    _mqttConnect();
  }

  void _senseData() {
      accelerometerSubscription = accelerometerEvents.listen((AccelerometerEvent aevent) {
        setState(() {
          _aevent = aevent;
        });
      });
      gyroscopeSubscription = gyroscopeEvents.listen((GyroscopeEvent gevent) {
        setState(() {
          _gevent = gevent;
        });
      });
      magnetometerSubscription = magnetometerEvents.listen((MagnetometerEvent mevent) {
        setState(() {
          _mevent = mevent;
        });
      });
  }

  void _stopSensing() {
    accelerometerSubscription.cancel();
    gyroscopeSubscription.cancel();
    magnetometerSubscription.cancel();
  }

  void _sendData(){
    _imuData = Data(
      tagID: _selectedChip.toString() + _address,
      accelerometer: [_aevent.x, _aevent.z, _aevent.z],
      gyroscope: [_gevent.x, _gevent.y, _gevent.z],
      magnetometer: [_mevent.x, _mevent.y, _mevent.z],
    );

    final builder1 = MqttClientPayloadBuilder();
    builder1.addString(jsonEncode(_imuData));
    try{
      client.publishMessage(topic1, MqttQos.exactlyOnce, builder1.payload);
    }on Exception catch (e) {
      print('client exception - $e');
    }
  }


  void _mqttConnect() {
    try {
      client.connect();
    } on Exception catch (e) {
      print('client exception - $e');
      client.disconnect();
      setState(() {
        _connected = false;
        if( _timer != null) _timer.cancel();
        _start = false;
      });
    }
  }

  void onConnected(){
    print('Connected to MQTT Broker');
    setState(() {
      _connected = true;
    });
  }

  void onDisconnected(){
    print('Disconnected');
    setState(() {
      _connected = false;
      if( _timer != null) _timer.cancel();
      _start = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        debugShowCheckedModeBanner: false,
        home: Scaffold(
          appBar: AppBar(
            title: const Text('DataSense'),
          ),
          body: SingleChildScrollView(
            padding: EdgeInsets.all(8.0),
            child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: <Widget>[
                  SingleChildScrollView(
                    primary: false,
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: //<Widget>[
                      List<Widget>.generate(
                        8,
                            (int idx) {
                          return Padding(
                            padding: const EdgeInsets.all(2.0),
                            child: ChoiceChip(
                                label: Text("Tag $idx"),
                                selectedColor: Colors.blue,
                                selected: _selectedChip == idx,
                                onSelected: (bool selected) {
                                  setState(() {
                                    _selectedChip = selected ? idx : -1;
                                  });
                                }),
                          );
                        },
                      ).toList(),
                    ),
                  ),
                  Visibility(
                    visible: _connected,
                    child: ListTile(
                        leading: _start == true
                            ? const Icon(Icons.start_outlined)
                            : const Icon(Icons.stop_circle_outlined),
                        title: Text(
                            _start == true ? "Status: Started" : "Status: Interrupted"),
                        subtitle: Text(_start == true
                            ? "Sending data to server"
                            : "Not sending data"),
                        trailing: ElevatedButton(
                            style:
                            ButtonStyle(backgroundColor: _selectedChip != -1 ?
                            const MaterialStatePropertyAll(Colors.blue):
                            const MaterialStatePropertyAll(Colors.black12)),
                            child: Text(_start == true ? "Interrupt" : "Start"),
                            onPressed: _selectedChip == -1 ? null: () {
                              setState(() {
                                _start = !_start;
                              });
                              if (_start) {
                                _senseData();
                                _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
                                  _sendData();
                                  print("periodic");
                                });
                              }else{
                                _stopSensing();
                                _timer.cancel();
                              }
                            }
                        )),
                  ),
                  Visibility(
                    visible: !_connected,
                    child: ListTile(
                        leading: const Icon(Icons.error_outline),
                        title: Text("Disconnected"),
                        subtitle: Text("Not connected to MQTT Broker"),
                        trailing: ElevatedButton(
                            child: Text("Connect"),
                            onPressed: () {
                              _mqttConnect();
                            }
                        )),
                  ),
                  Text(_selectedChip == -1
                      ? "No chip selected"
                      : "Selected MAC Address: $_selectedChip$_address"),
                  const Padding(padding: EdgeInsets.only(bottom: 8.0),),
                  Visibility(
                    visible: _timer != null && _timer.isActive,
                    child: InteractiveViewer(
                      panEnabled: false,
                      scaleEnabled: false,
                      child: DataTable(
                          columnSpacing: 10,
                          columns: const [
                            DataColumn(label: Text(
                                "Sensor",
                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                                ))),
                            DataColumn(label: Text(
                                "X",
                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                                ))),
                            DataColumn(label: Text(
                                "Y",
                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                                ))),
                            DataColumn(label: Text(
                                "Z",
                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                                ))),
                          ],
                          rows:  [
                            DataRow(cells: [
                              const DataCell(Text('Acceleromoter')),
                              DataCell(_aevent!=null? Text('${_aevent.x.toStringAsFixed(2)}'): Text("   ")),
                              DataCell(_aevent!=null? Text('${_aevent.y.toStringAsFixed(2)}'): Text("   ")),
                              DataCell(_aevent!=null? Text('${_aevent.z.toStringAsFixed(2)}'): Text("   ")),
                            ]),
                            DataRow(cells: [
                              const DataCell(Text('Gyroscope')),
                              DataCell(_gevent!=null? Text('${_gevent.x.toStringAsFixed(2)}'):Text("   ")),
                              DataCell(_gevent!=null? Text('${_gevent.y.toStringAsFixed(2)}'):Text("   ")),
                              DataCell(_gevent!=null? Text('${_gevent.z.toStringAsFixed(2)}'):Text("   ")),
                            ]),
                            DataRow(cells: [
                              const DataCell(Text('Magnetometer')),
                              DataCell(_mevent!=null? Text('${_mevent.x.toStringAsFixed(2)}'): Text("   ")),
                              DataCell(_mevent!=null? Text('${_mevent.y.toStringAsFixed(2)}'): Text("   ")),
                              DataCell(_mevent!=null? Text('${_mevent.z.toStringAsFixed(2)}'): Text("   ")),
                            ]),
                          ]
                      ),
                    ),
                  ),
                ]),
          ),
        ));
  }
}
