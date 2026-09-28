pragma Singleton
import QtQuick
import "."
Item {
    property var snapshot: { try{return JSON.parse(native.json)}catch(e){return {}} }
    FileState {id:native}
    function action(name,value){native.action(name,String(value??""))}
}
