import 'dart:convert';

class Data {
  String tagID;
  List<double> accelerometer;
  List<double> gyroscope;
  List<double> magnetometer;

  Data({this.tagID, this.accelerometer, this.gyroscope, this.magnetometer});

  Map<String, String> toJson() => {
        'T': tagID,
        'accelerometer':
            accelerometer == null ? null : jsonEncode(accelerometer),
        'gyroscope': gyroscope == null ? null : jsonEncode(gyroscope),
        'magnetometer': magnetometer == null ? null : jsonEncode(magnetometer),
      };

  @override
  String toString() {
    return '{'
        '"tagID":$tagID,'
        '"accelerometer":$accelerometer,'
        '"gyroscope":$gyroscope,'
        '"magnetometer":$magnetometer}';
  }
}
