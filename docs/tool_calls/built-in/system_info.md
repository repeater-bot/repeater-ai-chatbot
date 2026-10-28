# System Info

获取系统信息

注册名：`system_info`

返回当前的系统信息：
``` json
{
  "name": "Repeater AI System", // Repeater AI System Name
  "version": "x.x.x.x", // Repeater AI System Version
  "author": "Qeggs", // Repeater AI System Author
  "license": "MIT", // Repeater AI System License
  "copyright": "Copyright (c) 2025 Qeggs", // Repeater AI System Copyright
  "github": [...], // Repeater AI System Github Repositories
  "system_identificationConfig": {
    "system_name": "Repeater AI System", // Repeater AI System Name
    "system_ua": "Repeater AI System", // Repeater AI System User-Agent
    "crawler_name": "Repeater AI Crawler", // Repeater AI System Crawler Name
  },
  "platform": {
    "system": "", // The system/OS name, e.g. 'Linux', 'Windows' or 'Java'.
    "release": "", // The system's release, e.g. '2.2.0' or 'NT'
    "version": "", // The system's release version, e.g. '#3 on degas'
    "machine": "", // The machine type, e.g. 'i386'
    "processor": "" // The (true) processor name, e.g. 'amdk6'
  },
  "runtime": {
    "version": "Python 3.11.x (tags/v3.11.x:xxxxxx, xxx  x xxxx, xx:xx:xx) [Platform] on xxx", // Repeater AI System Runtime,
    "implementation": "CPython", // A string identifying the Python implementation.
    "version": "3.11.x", // The Python version as string 'major.minor.patchlevel'
    "compiler": "", // A string identifying the compiler used for compiling Python.
    "build": ["", ""], // A tuple (buildno, builddate) stating the Python build number and date as strings.
    "branch": "", // a string identifying the Python implementation branch. For CPython this is the SCM branch from which the Python binary was built. If not available, an empty string.
    "revision": "", // eturns a string identifying the Python implementation revision. For CPython this is the SCM revision from which the Python binary was built. If not available, an empty string.
  }
}
```

返回内容可被配置修改