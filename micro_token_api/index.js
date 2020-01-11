var Keycloak = require('keycloak-connect');
var hogan = require('hogan-express');
var express = require('express');
var session = require('express-session');
global.atob = require("atob");
const tokenAnalyse = require('./tokenAnalyse')
const apiAuth = require('./api_auth')
const rabbitMq = require('./rabbitMq')

var app = express();

const REDIRECTION_URL = 'https://app.updatr.tech/login/';

var server = app.listen(3000, function () {
  var host = server.address().address;
  var port = server.address().port;
  console.log('Serveur en écoute sur http://%s:%s', host, port);
});

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/view/index.html');
});

var memoryStore = new session.MemoryStore();

app.use(session({
  secret: 'mySecret',
  resave: false,
  saveUninitialized: true,
  store: memoryStore
}));

var keycloak = new Keycloak({
  store: memoryStore
});

app.use(keycloak.middleware({
  logout: '/auth/logout',
  admin: '/',
  protected: '/protected/resource'
}));

app.get('/auth/login', keycloak.protect(), function (req, res) {
  redirectToLoginRoute(res, dispathNewToken(JSON.parse(req.session['keycloak-token']), null, 4));
});

app.get('/api*', function (req, res) {
  printJson(res, apiAuth.setApi(req))
});

function redirectToLoginRoute(res, obj) {
  res.write('<script>window.location.href = "' + REDIRECTION_URL + obj.access_token + '";</script>');
  res.end();
}

function printJson(res, obj) {
  res.setHeader('Content-Type', 'application/json');
  res.write(JSON.stringify(obj))
  res.end()
}

function dispathNewToken(token) {
  tokenAnalyse.onLogin(token);
  rabbitMq.sendMessageToQueue(token.access_token);
  return token;
}