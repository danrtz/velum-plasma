// SPDX-License-Identifier: AGPL-3.0-or-later
#include <QGuiApplication>
#include <QQmlEngine>
#include <QQmlComponent>
#include <QQmlContext>
#include <QTimer>
#include <QFile>
#include <QVariant>
#include <QWaylandClientExtension>
#include <csignal>
#include <iostream>
#include "qwayland-screencast.h"
static volatile sig_atomic_t stopping=0;
class Stream : public QObject,public QtWayland::zkde_screencast_stream_unstable_v1 {
    Q_OBJECT
public: explicit Stream(struct ::zkde_screencast_stream_unstable_v1 *s):QtWayland::zkde_screencast_stream_unstable_v1(s){}
    ~Stream(){close();}
signals: void ready(uint node);void failed(QString error);
protected:
    void zkde_screencast_stream_unstable_v1_created(uint node) override{emit ready(node);}
    void zkde_screencast_stream_unstable_v1_failed(const QString &error) override{emit failed(error);}
    void zkde_screencast_stream_unstable_v1_closed() override{stopping=1;}
};
class Capture : public QWaylandClientExtensionTemplate<Capture>,public QtWayland::zkde_screencast_unstable_v1 {
public: Capture():QWaylandClientExtensionTemplate<Capture>(6){initialize();}
};
int main(int argc,char **argv){
    QGuiApplication app(argc,argv);
    app.setDesktopFileName("org.danrtz.velum.recorder");
    if(argc!=7){std::cerr<<"usage: velum-recorder x y width height scale output\n";return 2;}
    QCoreApplication::processEvents();
    Capture capture;
    QQmlEngine engine;
    const auto args=app.arguments();
    QObject *record=nullptr;Stream *stream=nullptr;
    auto start=[&]{
        if(stream||!capture.isActive())return;
        stream=new Stream(capture.stream_region(args[1].toInt(),args[2].toInt(),args[3].toUInt(),args[4].toUInt(),wl_fixed_from_double(args[5].toDouble()),2));
        QObject::connect(stream,&Stream::failed,&app,[&](QString error){std::cerr<<error.toStdString()<<'\n';app.exit(1);});
        QObject::connect(stream,&Stream::ready,&app,[&](uint node){
            engine.rootContext()->setContextProperty("captureNode",node);
            engine.rootContext()->setContextProperty("captureOutput",args[6]);
            QQmlComponent component(&engine);
            component.setData(R"(
                import QtQuick
                import org.kde.pipewire.record
                PipeWireRecord {
                    nodeId: captureNode
                    output: captureOutput
                    encoder: PipeWireRecord.H264Main
                    Component.onCompleted: start()
                    onErrorFound: error => {console.error(error);Qt.exit(1)}
                    onStateChanged: if(state===PipeWireRecord.Idle) Qt.quit()
                })",QUrl());
            record=component.create();
            if(!record){qWarning()<<component.errors();app.exit(1);return;}
            std::cout<<"RECORDING\n"<<std::flush;
        });
    };
    QObject::connect(&capture,&Capture::activeChanged,&app,start);
    QTimer::singleShot(0,&app,start);
    QTimer::singleShot(5000,&app,[&]{if(!stream){qWarning()<<"KWin recording interface unavailable. Check the recorder desktop entry.";app.exit(1);}});
    QObject::connect(&engine,&QQmlEngine::quit,&app,&QCoreApplication::quit);
    QObject::connect(&engine,&QQmlEngine::exit,&app,&QCoreApplication::exit);
    std::signal(SIGINT,[](int){stopping=1;});std::signal(SIGTERM,[](int){stopping=1;});
    QTimer tick;tick.setInterval(100);QObject::connect(&tick,&QTimer::timeout,&app,[&]{if(stopping&&record){stopping=0;QMetaObject::invokeMethod(record,"stop");QTimer::singleShot(10000,&app,&QCoreApplication::quit);}});tick.start();
    auto rc=app.exec();delete record;delete stream;return rc;
}
#include "main.moc"
