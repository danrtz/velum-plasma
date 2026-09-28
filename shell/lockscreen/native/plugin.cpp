// SPDX-License-Identifier: AGPL-3.0-or-later
#include <QQmlExtensionPlugin>
#include <QQmlEngine>
#include <QFileSystemWatcher>
#include <QFile>
#include <QDir>
#include <QJsonDocument>
#include <QJsonObject>
#include <QProcess>
class State : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString json READ json NOTIFY changed)
    QFileSystemWatcher watcher;
    QString payload = "{}", file;
public:
    explicit State(QObject *parent=nullptr):QObject(parent) {
        auto dir = qEnvironmentVariable("XDG_RUNTIME_DIR") + "/velum";
        file = dir + "/lock.json";
        watcher.addPath(dir);
        connect(&watcher,&QFileSystemWatcher::directoryChanged,this,[this]{read();});
        read();
    }
    QString json() const {return payload;}
    void read() {
        QFile f(file);
        if (!f.open(QIODevice::ReadOnly)) return;
        auto bytes=f.readAll();
        QJsonParseError error;
        auto doc=QJsonDocument::fromJson(bytes,&error);
        if(error.error!=QJsonParseError::NoError || !doc.isObject()) return;
        auto next=QString::fromUtf8(bytes);
        if(next!=payload){payload=next;emit changed();}
    }
    // Only desktop actions. Authentication stays entirely with KScreenLocker.
    Q_INVOKABLE void action(const QString &action,const QString &value=QString()) {
        const QStringList allowed={"keyboard","clear","dismiss","dismissGroup","markRead","previous","next","togglePlaying","scanNetwork","sound","markNotificationRead","notificationAction","setDnd"};
        if(!allowed.contains(action)) return;
        auto source=QJsonDocument::fromJson(payload.toUtf8()).object().value("source").toString();
        if(source.isEmpty()) return;
        QProcess::startDetached("quickshell",{"-p",source+"/quickshell/Shell.qml","ipc","call","lockState","action",action,value});
    }
signals:
    void changed();
};
class Plugin : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char *uri) override {qmlRegisterType<State>(uri,1,0,"FileState");}
};
#include "plugin.moc"
