pragma Singleton
import QtQuick
import "."
QtObject {function t(key,args){let s=(NativeState.snapshot.translations||{})[key]||key;for(let k in args)s=s.replace(new RegExp("\\{"+k+"\\}","g"),args[k]);return s}}
