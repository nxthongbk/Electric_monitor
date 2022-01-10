import 'package:flutter/material.dart';
import 'package:flutter_login/flutter_login.dart';
import 'dashboard_screen.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/io.dart';
import 'package:shared_preferences/shared_preferences.dart';

String uRl = "wss://octave-ws.sierrawireless.io/session/";
final String end1 = "/ws";

class Album {
  final String id;
  Album({this.id});
  factory Album.fromJson(Map<String, dynamic> json) {
    return Album(
        id: json['body']['id']
    );
  }
}

class LoginScreen extends StatelessWidget {
  String str1;
  String str2;
  WebSocketChannel channel;
  Duration get loginTime => Duration(milliseconds: 2250);

  Future<String> createAlbum(LoginData data) async {
    String url = 'https://octave-ws.sierrawireless.io/session';
    Map<String, String> header = {
      'Content-Type': 'application/json; charset=UTF-8; none',
      'X-Auth-User': '${(data.name).split('@')[0]}',
      'X-Auth-Token': 'qrKEUoYZiOrgdhuYJXwmqlBwZcDfFOJi',
      'X-Auth-Company': 'tma_solutions'
    };

    final http.Response response = await http.post(url, headers: header);
    return Future.delayed(loginTime).then((_) {
      if (response.statusCode != 201) {
        return 'Username not exists';
      }
      if (data.password != "12345") {
        return 'Password does not match';
      }
      if ((data.name).split('@')[1] != "tma.com.vn") {
        return 'Username not exists';
      }
      str1 = jsonDecode(response.body)['body']['id'];
      channel = IOWebSocketChannel.connect(uRl+str1+end1);
      return null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return FlutterLogin(
      title: 'Electric Monitor',
      logo: 'assets/images/Logo.png',
      onLogin: createAlbum,
      onSignup: (_) => Future(null),
      onSubmitAnimationCompleted: () {
        Navigator.of(context).pushReplacement(MaterialPageRoute(
          builder: (context) => DashboardScreen(channel: channel),
        ));
      },
      onRecoverPassword: (_) => Future(null),
    );
  }
}