## Multi-Platform Log Analysis Training Dataset

**Purpose:** Training dataset for log analysis, monitoring, and incident detection

---

## Table of Contents
1. [Veggo Spring Project Logs](#1-veggo-spring-project-logs)
2. [Code Editor Logs](#2-code-editor-logs)
3. [Istio Service Mesh Logs](#3-istio-service-mesh-logs)
4. [WildFly/JBoss Logs](#4-wildflyjboss-logs)
5. [Tomcat Logs](#5-tomcat-logs)
6. [Nginx Logs](#6-nginx-logs)
7. [Node.js Application Logs](#7-nodejs-application-logs)
8. [Kubernetes Metrics & Logs](#8-kubernetes-metrics--logs)
9. [Incident Scenarios](#9-incident-scenarios)

---

## 1. Veggo Spring Project Logs

### Log Format Structure
```
<Timestamp> |<Application> : <LogLevel> |<ThreadPool>-[<ThreadID>]: |<CorrelationID>| <TenantInfo>:<Username> | tenantID:<TenantID>: <Action> for project:<ProjectID> username: <Username> organization: <Organization>
```

### Log Field Descriptions
| Field | Description | Example |
|-------|-------------|---------|
| Timestamp | Date and time with milliseconds | `Mar 25, 2026 15:03:16:423` |
| Application | Application name | `organisationValue` |
| LogLevel | Severity level (INFO, WARN, ERROR, DEBUG) | `INFO` |
| ThreadPool | Thread pool identifier | `default` |
| ThreadID | Thread identifier | `pool-9-thread-1` |
| CorrelationID | UUID for request tracing | `f03dfc7d-8686-4681-a33e-9146e7a7d3b0` |
| Username | User performing the action | `john.doe` |
| TenantID | Multi-tenant identifier | `tenant-001` |
| ProjectID | Project identifier | `proj-12345` |
| Organization | Organization name | `ACME-Corp` |

### Normal Operation Examples
```log
Mar 25, 2026 15:03:16:423 |organisationValue : INFO |default-[pool-9-thread-1]: |f03dfc7d-8686-4681-a33e-9146e7a7d3b0| null:john.doe | tenantID:tenant-001: REMOVE_STATUS for project:proj-12345 username: john.doe organization: ACME-Corp

Mar 25, 2026 15:03:17:891 |organisationValue : INFO |default-[pool-9-thread-2]: |a1b2c3d4-5678-90ab-cdef-1234567890ab| null:sarah.smith | tenantID:tenant-002: CREATE_PROJECT for project:proj-67890 username: sarah.smith organization: TechStart

Mar 25, 2026 15:03:18:245 |organisationValue : INFO |default-[pool-9-thread-3]: |e5f6a7b8-9012-34cd-ef56-7890abcdef12| null:mike.wilson | tenantID:tenant-001: UPDATE_CONFIG for project:proj-12345 username: mike.wilson organization: ACME-Corp

Mar 25, 2026 15:03:19:112 |organisationValue : DEBUG |default-[pool-9-thread-1]: |f03dfc7d-8686-4681-a33e-9146e7a7d3b0| null:john.doe | tenantID:tenant-001: DATABASE_QUERY executed in 45ms for project:proj-12345 username: john.doe organization: ACME-Corp

Mar 25, 2026 15:03:20:567 |organisationValue : INFO |default-[pool-9-thread-4]: |b9c0d1e2-3456-78fa-bcde-f01234567890| null:emma.jones | tenantID:tenant-003: DEPLOY_APPLICATION for project:proj-11111 username: emma.jones organization: GlobalTech

Mar 25, 2026 15:03:21:789 |organisationValue : INFO |default-[pool-9-thread-5]: |c4d5e6f7-8901-23ab-cdef-456789012345| null:david.brown | tenantID:tenant-001: BUILD_SUCCESS for project:proj-22222 username: david.brown organization: ACME-Corp

Mar 25, 2026 15:03:22:345 |organisationValue : INFO |async-[pool-12-thread-1]: |d8e9f0a1-2345-67bc-def0-123456789abc| null:lisa.taylor | tenantID:tenant-004: SYNC_REPOSITORY for project:proj-33333 username: lisa.taylor organization: DataCorp
```

### Warning Examples
```log
Mar 25, 2026 15:04:01:234 |organisationValue : WARN |default-[pool-9-thread-2]: |a1b2c3d4-5678-90ab-cdef-1234567890ab| null:sarah.smith | tenantID:tenant-002: SLOW_QUERY detected (2345ms) for project:proj-67890 username: sarah.smith organization: TechStart

Mar 25, 2026 15:04:15:567 |organisationValue : WARN |default-[pool-9-thread-3]: |e5f6a7b8-9012-34cd-ef56-7890abcdef12| null:mike.wilson | tenantID:tenant-001: CONNECTION_POOL_LOW (available: 5/100) for project:proj-12345 username: mike.wilson organization: ACME-Corp

Mar 25, 2026 15:04:30:891 |organisationValue : WARN |async-[pool-12-thread-2]: |f1a2b3c4-5678-90de-f012-34567890abcd| null:admin.user | tenantID:null: MEMORY_THRESHOLD_WARNING heap_usage:85% for project:system username: admin.user organization: system
```

### Error Examples
```log
Mar 25, 2026 15:05:01:123 |organisationValue : ERROR |default-[pool-9-thread-1]: |f03dfc7d-8686-4681-a33e-9146e7a7d3b0| null:john.doe | tenantID:tenant-001: DATABASE_CONNECTION_FAILED for project:proj-12345 username: john.doe organization: ACME-Corp - java.sql.SQLException: Connection timed out

Mar 25, 2026 15:05:15:456 |organisationValue : ERROR |default-[pool-9-thread-4]: |b9c0d1e2-3456-78fa-bcde-f01234567890| null:emma.jones | tenantID:tenant-003: DEPLOYMENT_FAILED for project:proj-11111 username: emma.jones organization: GlobalTech - Kubernetes API returned 503

Mar 25, 2026 15:05:30:789 |organisationValue : ERROR |async-[pool-12-thread-3]: |g2h3i4j5-6789-01kl-mnop-qrstuvwxyz12| null:system | tenantID:null: OUT_OF_MEMORY_ERROR heap exhausted for project:all username: system organization: system - java.lang.OutOfMemoryError: Java heap space
```

---

## 2. Code Editor Logs

### Startup Sequence
```log
─────────────────────────────────────── GID/UID ───────────────────────────────────────
User UID: 1000
User GID: 1000
─────────────────────────────────────── Linuxserver.io version: 4.108.2-ls314
Build-date: 2026-01-26T22:53:13+00:00
───────────────────────────────────────
Change in ownership or new install detected, please be patient while we chown existing files
This could take some time
[custom-init] No custom files found, skipping...
Executing setup.ps1...
[GitHub Copilot Chat Export - Global Setup]
=============================================
[1/4] Creating template directory...
Created: /home/project/code-server/.git-templates
[2/4] Installing capture script...
Installed: /home/project/code-server/.git-templates/capture-copilot-data.ps1
[3/4] Creating pre-commit hook...
Created: /home/project/code-server/.git-templates/hooks/pre-commit
[4/4] Configuring git globally...
Set: core.hooksPath = /home/project/code-server/.git-templates/hooks
Set: init.templateDir = /home/project/code-server/.git-templates
=============================================
[SUCCESS] Global setup complete!
=============================================
```

### Server Running Logs
```log
[2026-03-25T15:07:15.977Z] info  code-server 4.108.2 3c0b449c6e6e37b44a8a7938c0d8a3049926a64c
[2026-03-25T15:07:15.981Z] info  Using user-data-dir /home/project/code-server/data
[2026-03-25T15:07:16.015Z] info  Using config file /home/project/code-server/.config/code-server/config.yaml
[2026-03-25T15:07:16.016Z] info  HTTP server listening on http://0.0.0.0:8443/
[2026-03-25T15:07:16.017Z] info    - Authentication is disabled
[2026-03-25T15:07:16.018Z] info    - Not serving HTTPS
[2026-03-25T15:07:16.018Z] info  Session server listening on /home/project/code-server/data/code-server-ipc.sock
Connection to 192.168.1.100 8443 port [tcp/*] succeeded!
[ls.io-init] done.
```

### Extension Loading Logs
```log
[2026-03-25T15:07:19.012Z] info  Extension host started successfully
[2026-03-25T15:07:19.345Z] info  Language server for Python started
[2026-03-25T15:07:19.678Z] warn  Extension vscode-icons: deprecated API usage detected
[2026-03-25T15:07:20.001Z] error Extension my-broken-ext: Failed to activate - TypeError: Cannot read property 'undefined'
```

---

## 3. Istio Service Mesh Logs

### Proxy Initialization
```log
2026-03-25T15:07:11.742088Z	info	FLAG: --help="false"
2026-03-25T15:07:11.742093Z	info	FLAG: --log_as_json="false"
2026-03-25T15:07:11.742099Z	info	FLAG: --log_caller=""
2026-03-25T15:07:11.742104Z	info	FLAG: --log_output_level="default:info"
2026-03-25T15:07:11.742109Z	info	FLAG: --log_rotate=""
2026-03-25T15:07:11.742114Z	info	FLAG: --log_rotate_max_age="30"
2026-03-25T15:07:11.742120Z	info	FLAG: --log_rotate_max_backups="1000"
2026-03-25T15:07:11.742185Z	info	FLAG: --log_rotate_max_size="104857600"
2026-03-25T15:07:11.742281Z	info	FLAG: --log_stacktrace_level="default:none"
2026-03-25T15:07:11.742338Z	info	FLAG: --log_target="[stdout]"
2026-03-25T15:07:11.742380Z	info	FLAG: --meshConfig="./etc/istio/config/mesh"
2026-03-25T15:07:11.742450Z	info	FLAG: --outlierLogPath=""
2026-03-25T15:07:11.742462Z	info	FLAG: --proxyComponentLogLevel="misc:error"
2026-03-25T15:07:11.742468Z	info	FLAG: --proxyLogLevel="warning"
2026-03-25T15:07:11.742474Z	info	FLAG: --serviceCluster="istio-proxy"
2026-03-25T15:07:11.742480Z	info	FLAG: --stsPort="0"
2026-03-25T15:07:11.742520Z	info	FLAG: --templateFile=""
2026-03-25T15:07:11.742545Z	info	FLAG: --tokenManagerPlugin="GoogleTokenExchange"
2026-03-25T15:07:11.742554Z	info	FLAG: --vklog="0"
2026-03-25T15:07:11.742561Z	info	Version 1.18.2-distroless-Clean
2026-03-25T15:07:11.748424Z	info	Maximum file descriptors (ulimit -n): 1048576
2026-03-25T15:07:11.748972Z	info	Proxy role	ips=[10.244.0.15] type=sidecar id=john-tr-codeeditor-6f658cb5d5-c9rxc.organisationValue domain=cluster.local
2026-03-25T15:07:11.749188Z	info	Apply proxy config from env	{}
2026-03-25T15:07:11.752927Z	info	Effective config: binaryPath: /usr/local/bin/envoy
```

### Traffic Routing Logs
```log
2026-03-25T15:08:00.123456Z	info	xdsproxy	connected to upstream XDS server: istiod.istio-system.svc:15012
2026-03-25T15:08:00.234567Z	info	ads	ADS: new]connection for node:john-tr-codeeditor-6f658cb5d5-c9rxc.organisationValue-1
2026-03-25T15:08:00.345678Z	info	ads	CDS: PUSH request for node:john-tr-codeeditor-6f658cb5d5-c9rxc.organisationValue resources:156
2026-03-25T15:08:00.456789Z	info	ads	EDS: PUSH request for node:john-tr-codeeditor-6f658cb5d5-c9rxc.organisationValue resources:89
2026-03-25T15:08:00.567890Z	info	ads	LDS: PUSH request for node:john-tr-codeeditor-6f658cb5d5-c9rxc.organisationValue resources:23
2026-03-25T15:08:00.678901Z	info	ads	RDS: PUSH request for node:john-tr-codeeditor-6f658cb5d5-c9rxc.organisationValue resources:12
```

### Circuit Breaker Events
```log
2026-03-25T15:10:15.123456Z	warn	envoy	upstream_cx_overflow	cluster=outbound|8080||cluster.name.example.value
2026-03-25T15:10:15.234567Z	warn	envoy	upstream_rq_pending_overflow	cluster=outbound|8080||cluster.name.example.value
2026-03-25T15:10:16.345678Z	error	envoy	circuit breaker tripped for cluster outbound|8080||cluster.name.example.value
2026-03-25T15:10:45.456789Z	info	envoy	circuit breaker recovered for cluster outbound|8080||cluster.name.example.value
```

---

## 4. WildFly/JBoss Logs

### Server Startup
```log
=========================================================================

  JBoss Bootstrap Environment

  JBOSS_HOME: /opt/wildfly-27.0.1.Final

  JAVA: /usr/lib/jvm/java-17-openjdk/bin/java

  JAVA_OPTS:  -server -Xms1024m -Xmx2048m -XX:MetaspaceSize=256m

=========================================================================

2026-03-25 15:00:00,001 INFO  [org.jboss.modules] (main) JBoss Modules version 2.1.0.Final
2026-03-25 15:00:00,456 INFO  [org.jboss.msc] (main) JBoss MSC version 1.5.0.Final
2026-03-25 15:00:00,789 INFO  [org.jboss.as] (MSC service thread 1-1) WFLYSRV0049: WildFly Full 27.0.1.Final (WildFly Core 19.0.1.Final) starting
2026-03-25 15:00:05,123 INFO  [org.jboss.as.server] (Controller Boot Thread) WFLYSRV0039: Creating http management service using socket-binding (management-http)
2026-03-25 15:00:05,456 INFO  [org.xnio] (MSC service thread 1-2) XNIO version 3.8.8.Final
2026-03-25 15:00:05,789 INFO  [org.xnio.nio] (MSC service thread 1-2) XNIO NIO Implementation Version 3.8.8.Final
2026-03-25 15:00:06,012 INFO  [org.jboss.remoting] (MSC service thread 1-2) JBoss Remoting version 5.0.25.Final
2026-03-25 15:00:08,345 INFO  [org.wildfly.extension.undertow] (ServerService Thread Pool -- 80) WFLYUT0021: Registered web context: '/organisationValue-api' for server 'default-server'
2026-03-25 15:00:10,678 INFO  [org.jboss.as.server] (ServerService Thread Pool -- 45) WFLYSRV0010: Deployed "organisationValue-api.war" (runtime-name : "organisationValue-api.war")
2026-03-25 15:00:12,001 INFO  [org.jboss.as] (Controller Boot Thread) WFLYSRV0025: WildFly Full 27.0.1.Final (WildFly Core 19.0.1.Final) started in 12001ms
```

### Application Processing
```log
2026-03-25 15:03:00,123 INFO  [com.vermeg.organisationValue.BusinessService] (default task-1) Processing request for user: john.doe, correlationId: f03dfc7d-8686-4681-a33e-9146e7a7d3b0
2026-03-25 15:03:00,234 INFO  [com.vermeg.organisationValue.DatabasePool] (default task-1) Acquired connection from pool (active: 25/100)
2026-03-25 15:03:00,567 INFO  [com.vermeg.organisationValue.PositionService] (default task-1) Creating position for client: CLIENT-001 in project: proj-12345
2026-03-25 15:03:01,123 INFO  [com.vermeg.organisationValue.EventService] (default task-1) Event published: POSITION_CREATED, eventId: evt-98765
2026-03-25 15:03:01,456 INFO  [com.vermeg.organisationValue.DatabasePool] (default task-1) Connection returned to pool (active: 24/100)
```

### JPA/Hibernate Logs
```log
2026-03-25 15:03:02,001 DEBUG [org.hibernate.SQL] (default task-2) select p1_0.id,p1_0.client_id,p1_0.position_type from position p1_0 where p1_0.client_id=?
2026-03-25 15:03:02,123 DEBUG [org.hibernate.type.descriptor.sql.BasicBinder] (default task-2) binding parameter [1] as [VARCHAR] - [CLIENT-001]
2026-03-25 15:03:02,234 TRACE [org.hibernate.stat.internal.StatisticsImpl] (default task-2) Query executed in 45ms, rows returned: 156
2026-03-25 15:03:02,345 WARN  [org.hibernate.engine.jdbc.spi.SqlExceptionHelper] (default task-3) SQL Warning Code: 0, SQLState: 01000 - Query execution time exceeded threshold
```

### Datasource Warnings/Errors
```log
2026-03-25 15:04:00,001 WARN  [org.jboss.jca.adapters.jdbc.local.LocalManagedConnectionFactory] (JCA PoolFiller) IJ000604: Filling pool of datasource: java:jboss/datasources/organisationValueDS low on connections (available: 3)
2026-03-25 15:04:30,234 ERROR [org.jboss.jca.core.connectionmanager.pool.strategy.OnePool] (default task-10) IJ000453: Unable to get managed connection for java:jboss/datasources/organisationValueDS
2026-03-25 15:04:30,345 ERROR [com.vermeg.organisationValue.BusinessService] (default task-10) Database connection timeout after 30000ms, correlationId: a1b2c3d4-5678-90ab-cdef-1234567890ab
```

---

## 5. Tomcat Logs

### Catalina Startup
```log
25-Mar-2026 15:00:00.001 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log Server version name:   Apache Tomcat/10.1.18
25-Mar-2026 15:00:00.005 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log Server built:          Jan 15 2026 12:00:00 UTC
25-Mar-2026 15:00:00.006 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log Server version number: 10.1.18.0
25-Mar-2026 15:00:00.007 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log OS Name:               Linux
25-Mar-2026 15:00:00.008 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log OS Version:            5.15.0-91-generic
25-Mar-2026 15:00:00.009 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log Architecture:          amd64
25-Mar-2026 15:00:00.010 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log Java Home:             /usr/lib/jvm/java-17-openjdk-amd64
25-Mar-2026 15:00:00.100 INFO [main] org.apache.catalina.startup.VersionLoggerListener.log JVM Version:           17.0.9+9-Ubuntu-122.04
25-Mar-2026 15:00:01.234 INFO [main] org.apache.catalina.core.AprLifecycleListener.lifecycleEvent Loaded Apache Tomcat Native library [2.0.5] using APR version [1.7.2]
25-Mar-2026 15:00:01.567 INFO [main] org.apache.catalina.core.AprLifecycleListener.lifecycleEvent APR capabilities: IPv6 [true], sendfile [true], accept filters [false], random [true], UDS [true]
25-Mar-2026 15:00:02.123 INFO [main] org.apache.coyote.AbstractProtocol.init Initializing ProtocolHandler ["http-nio-8080"]
25-Mar-2026 15:00:02.456 INFO [main] org.apache.catalina.startup.Catalina.load Server initialization in [2456] milliseconds
25-Mar-2026 15:00:02.789 INFO [main] org.apache.catalina.core.StandardService.startInternal Starting service [Catalina]
25-Mar-2026 15:00:02.890 INFO [main] org.apache.catalina.core.StandardEngine.startInternal Starting Servlet engine: [Apache Tomcat/10.1.18]
25-Mar-2026 15:00:05.123 INFO [main] org.apache.catalina.startup.HostConfig.deployWAR Deploying web application archive [/opt/tomcat/webapps/organisationValue-web.war]
25-Mar-2026 15:00:08.456 INFO [main] org.apache.catalina.startup.HostConfig.deployWAR Deployment of web application archive [/opt/tomcat/webapps/organisationValue-web.war] has finished in [3,333] ms
25-Mar-2026 15:00:08.567 INFO [main] org.apache.coyote.AbstractProtocol.start Starting ProtocolHandler ["http-nio-8080"]
25-Mar-2026 15:00:08.678 INFO [main] org.apache.catalina.startup.Catalina.start Server startup in [5889] milliseconds
```

### Access Logs (Combined Format)
```log
192.168.1.50 - john.doe [25/Mar/2026:15:03:16 +0000] "GET /organisationValue-web/api/positions?clientId=CLIENT-001 HTTP/1.1" 200 4523 "https://organisationValue.acme-corp.com/dashboard" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
192.168.1.51 - sarah.smith [25/Mar/2026:15:03:17 +0000] "POST /organisationValue-web/api/projects HTTP/1.1" 201 1234 "https://organisationValue.techstart.com/projects" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.52 - mike.wilson [25/Mar/2026:15:03:18 +0000] "PUT /organisationValue-web/api/config/proj-12345 HTTP/1.1" 200 567 "https://organisationValue.acme-corp.com/settings" "Mozilla/5.0 (X11; Linux x86_64)"
192.168.1.53 - - [25/Mar/2026:15:03:19 +0000] "GET /organisationValue-web/health HTTP/1.1" 200 15 "-" "kube-probe/1.28"
192.168.1.54 - emma.jones [25/Mar/2026:15:03:20 +0000] "POST /organisationValue-web/api/deploy HTTP/1.1" 500 2345 "https://organisationValue.globaltech.com/deploy" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
10.0.0.1 - - [25/Mar/2026:15:03:21 +0000] "GET /organisationValue-web/api/metrics HTTP/1.1" 200 8901 "-" "Prometheus/2.45.0"
```

### Thread Pool Logs
```log
25-Mar-2026 15:04:00.123 WARNING [http-nio-8080-exec-200] org.apache.tomcat.util.threads.TaskQueue.offer All threads [200] are currently busy, waiting.
25-Mar-2026 15:04:01.234 WARNING [http-nio-8080-exec-200] org.apache.tomcat.util.threads.TaskQueue.offer Request queue depth: 50
25-Mar-2026 15:04:15.456 WARNING [ContainerBackgroundProcessor[StandardEngine[Catalina]]] org.apache.catalina.core.StandardContext.backgroundProcess A long-running request [/organisationValue-web/api/reports/generate] blocked processing thread [http-nio-8080-exec-15] for 45123ms
```

---

## 6. Nginx Logs

### Access Logs (JSON Format)
```json
{"time_local":"25/Mar/2026:15:03:16 +0000","remote_addr":"192.168.1.50","remote_user":"john.doe","request":"GET /api/v1/positions HTTP/1.1","status":"200","body_bytes_sent":"4523","request_time":"0.045","http_referer":"https://organisationValue.acme-corp.com/dashboard","http_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)","http_x_forwarded_for":"203.0.113.50","upstream_response_time":"0.042","upstream_addr":"10.244.0.15:8080","request_id":"f03dfc7d-8686-4681-a33e-9146e7a7d3b0"}
{"time_local":"25/Mar/2026:15:03:17 +0000","remote_addr":"192.168.1.51","remote_user":"sarah.smith","request":"POST /api/v1/projects HTTP/1.1","status":"201","body_bytes_sent":"1234","request_time":"0.156","http_referer":"https://organisationValue.techstart.com/projects","http_user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)","http_x_forwarded_for":"198.51.100.51","upstream_response_time":"0.152","upstream_addr":"10.244.0.16:8080","request_id":"a1b2c3d4-5678-90ab-cdef-1234567890ab"}
{"time_local":"25/Mar/2026:15:03:18 +0000","remote_addr":"192.168.1.52","remote_user":"mike.wilson","request":"PUT /api/v1/config/proj-12345 HTTP/1.1","status":"200","body_bytes_sent":"567","request_time":"0.089","http_referer":"https://organisationValue.acme-corp.com/settings","http_user_agent":"Mozilla/5.0 (X11; Linux x86_64)","http_x_forwarded_for":"203.0.113.52","upstream_response_time":"0.085","upstream_addr":"10.244.0.15:8080","request_id":"e5f6a7b8-9012-34cd-ef56-7890abcdef12"}
{"time_local":"25/Mar/2026:15:03:20 +0000","remote_addr":"192.168.1.54","remote_user":"emma.jones","request":"POST /api/v1/deploy HTTP/1.1","status":"502","body_bytes_sent":"234","request_time":"30.001","http_referer":"https://organisationValue.globaltech.com/deploy","http_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)","http_x_forwarded_for":"203.0.113.54","upstream_response_time":"30.000","upstream_addr":"10.244.0.17:8080","request_id":"b9c0d1e2-3456-78fa-bcde-f01234567890"}
```

### Error Logs
```log
2026/03/25 15:03:20 [error] 12345#12345: *67890 upstream timed out (110: Connection timed out) while reading response header from upstream, client: 192.168.1.54, server: organisationValue.globaltech.com, request: "POST /api/v1/deploy HTTP/1.1", upstream: "http://10.244.0.17:8080/api/v1/deploy", host: "organisationValue.globaltech.com"
2026/03/25 15:04:00 [warn] 12345#12345: *67891 an upstream response is buffered to a temporary file /var/cache/nginx/proxy_temp/1/00/0000000001, client: 192.168.1.55, server: organisationValue.acme-corp.com, request: "GET /api/v1/reports/large HTTP/1.1"
2026/03/25 15:04:30 [error] 12345#12345: *67892 connect() failed (111: Connection refused) while connecting to upstream, client: 192.168.1.56, server: organisationValue.techstart.com, request: "GET /api/v1/health HTTP/1.1", upstream: "http://10.244.0.18:8080/api/v1/health", host: "organisationValue.techstart.com"
2026/03/25 15:05:00 [crit] 12345#12345: *67893 SSL_do_handshake() failed (SSL: error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure), client: 192.168.1.57, server: 0.0.0.0:443
2026/03/25 15:05:30 [emerg] 12345#12345: worker_connections are not enough, reusing connection
```

### Upstream Health Checks
```log
2026/03/25 15:06:00 [notice] 12345#12345: upstream server 10.244.0.15:8080 is up
2026/03/25 15:06:00 [notice] 12345#12345: upstream server 10.244.0.16:8080 is up
2026/03/25 15:06:00 [warn] 12345#12345: upstream server 10.244.0.17:8080 is down
2026/03/25 15:06:30 [notice] 12345#12345: upstream server 10.244.0.17:8080 recovered, enabling server
```

---

## 7. Node.js Application Logs

### Application Startup (Winston/Pino Format)
```json
{"level":"info","time":"2026-03-25T15:00:00.123Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Starting organisationValue Node API v2.5.0","version":"2.5.0","nodeVersion":"v20.11.0"}
{"level":"info","time":"2026-03-25T15:00:00.456Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Connecting to database","host":"postgres-test.database.test.cluster.test","port":5432,"database":"organisationValue_db"}
{"level":"info","time":"2026-03-25T15:00:01.234Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Database connection established","poolSize":20,"connectionTime":"778ms"}
{"level":"info","time":"2026-03-25T15:00:01.567Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Connecting to Redis","host":"redis-master.cache.svc.cluster.local","port":6379}
{"level":"info","time":"2026-03-25T15:00:01.789Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Redis connection established","latency":"222ms"}
{"level":"info","time":"2026-03-25T15:00:02.012Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Loading middleware","middlewares":["cors","helmet","compression","morgan","rateLimit"]}
{"level":"info","time":"2026-03-25T15:00:02.345Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"HTTP server listening","port":3000,"env":"production"}
```

### Request Processing
```json
{"level":"info","time":"2026-03-25T15:03:16.123Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","correlationId":"f03dfc7d-8686-4681-a33e-9146e7a7d3b0","msg":"Incoming request","method":"GET","url":"/api/v2/positions","userId":"john.doe","tenantId":"tenant-001","organization":"ACME-Corp","ip":"192.168.1.50"}
{"level":"debug","time":"2026-03-25T15:03:16.234Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","correlationId":"f03dfc7d-8686-4681-a33e-9146e7a7d3b0","msg":"Cache miss","key":"positions:CLIENT-001"}
{"level":"debug","time":"2026-03-25T15:03:16.345Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","correlationId":"f03dfc7d-8686-4681-a33e-9146e7a7d3b0","msg":"Database query executed","query":"SELECT * FROM positions WHERE client_id = $1","duration":"89ms","rowCount":156}
{"level":"info","time":"2026-03-25T15:03:16.456Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","correlationId":"f03dfc7d-8686-4681-a33e-9146e7a7d3b0","msg":"Response sent","statusCode":200,"responseTime":"333ms","contentLength":4523}
```

### Error Scenarios
```json
{"level":"error","time":"2026-03-25T15:05:01.123Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","correlationId":"g2h3i4j5-6789-01kl-mnop-qrstuvwxyz12","msg":"Unhandled error in request handler","error":{"name":"DatabaseError","message":"Connection terminated unexpectedly","code":"57P01","stack":"DatabaseError: Connection terminated unexpectedly\n    at Client._handleErrorMessage (/app/node_modules/pg/lib/client.js:315:17)\n    at Connection.emit (node:events:517:28)"}}
{"level":"warn","time":"2026-03-25T15:05:02.234Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","correlationId":"h3i4j5k6-7890-12mn-opqr-stuvwxyz1234","msg":"Rate limit exceeded","userId":"bot-scraper","ip":"198.51.100.99","limit":100,"window":"15m"}
{"level":"error","time":"2026-03-25T15:05:03.345Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Memory threshold exceeded","heapUsed":"1.8GB","heapTotal":"2.0GB","rss":"2.5GB","external":"156MB","alert":"HIGH_MEMORY_USAGE"}
{"level":"fatal","time":"2026-03-25T15:05:30.456Z","pid":1,"hostname":"organisationValue-node-api-7d5f8c6b4d-x2k9m","msg":"Process out of memory, initiating graceful shutdown","heapUsed":"1.95GB","heapTotal":"2.0GB"}
```

### PM2 Process Manager Logs
```log
PM2        | 2026-03-25T15:00:00.000Z: [PM2] Spawning PM2 daemon with pm2_home=/home/node/.pm2
PM2        | 2026-03-25T15:00:00.500Z: [PM2] PM2 Successfully daemonized
PM2        | 2026-03-25T15:00:01.000Z: [PM2] Starting /app/server.js in cluster_mode (4 instances)
PM2        | 2026-03-25T15:00:02.000Z: [PM2] App [organisationValue-api:0] online
PM2        | 2026-03-25T15:00:02.100Z: [PM2] App [organisationValue-api:1] online
PM2        | 2026-03-25T15:00:02.200Z: [PM2] App [organisationValue-api:2] online
PM2        | 2026-03-25T15:00:02.300Z: [PM2] App [organisationValue-api:3] online
PM2        | 2026-03-25T15:05:30.456Z: [PM2][WARN] Process [organisationValue-api:2] consuming too much memory (2.1GB > 2.0GB), restarting
PM2        | 2026-03-25T15:05:31.000Z: [PM2] Stopping app [organisationValue-api:2]
PM2        | 2026-03-25T15:05:32.000Z: [PM2] Starting app [organisationValue-api:2]
PM2        | 2026-03-25T15:05:33.000Z: [PM2] App [organisationValue-api:2] online
```

---

## 8. Kubernetes Metrics & Logs

### Pod Events
```log
2026-03-25T15:00:00.000Z	Normal	Scheduled	pod/organisationValue-api-6f658cb5d5-c9rxc	Successfully assigned organisationValue/organisationValue-api-6f658cb5d5-c9rxc to node-worker-01
2026-03-25T15:00:01.000Z	Normal	Pulling	pod/organisationValue-api-6f658cb5d5-c9rxc	Pulling image "registry.acme-corp.com/organisationValue-api:v2.5.0"
2026-03-25T15:00:05.000Z	Normal	Pulled	pod/organisationValue-api-6f658cb5d5-c9rxc	Successfully pulled image "registry.acme-corp.com/organisationValue-api:v2.5.0" in 4.123s
2026-03-25T15:00:05.500Z	Normal	Created	pod/organisationValue-api-6f658cb5d5-c9rxc	Created container organisationValue-api
2026-03-25T15:00:06.000Z	Normal	Started	pod/organisationValue-api-6f658cb5d5-c9rxc	Started container organisationValue-api
2026-03-25T15:00:20.000Z	Warning	Unhealthy	pod/organisationValue-api-6f658cb5d5-c9rxc	Readiness probe failed: HTTP probe failed with statuscode: 503
2026-03-25T15:00:30.000Z	Normal	Healthy	pod/organisationValue-api-6f658cb5d5-c9rxc	Readiness probe succeeded
```

### Deployment Events
```log
2026-03-25T14:55:00.000Z	Normal	ScalingReplicaSet	deployment/organisationValue-api	Scaled up replica set organisationValue-api-6f658cb5d5 to 3
2026-03-25T14:55:01.000Z	Normal	SuccessfulCreate	replicaset/organisationValue-api-6f658cb5d5	Created pod: organisationValue-api-6f658cb5d5-c9rxc
2026-03-25T14:55:01.100Z	Normal	SuccessfulCreate	replicaset/organisationValue-api-6f658cb5d5	Created pod: organisationValue-api-6f658cb5d5-k7mnd
2026-03-25T14:55:01.200Z	Normal	SuccessfulCreate	replicaset/organisationValue-api-6f658cb5d5	Created pod: organisationValue-api-6f658cb5d5-p2qrs
```

### HPA (Horizontal Pod Autoscaler) Events
```log
2026-03-25T15:10:00.000Z	Normal	SuccessfulRescale	horizontalpodautoscaler/organisationValue-api	New size: 5; reason: cpu resource utilization (percentage of request) above target
2026-03-25T15:10:00.500Z	Normal	ScalingReplicaSet	deployment/organisationValue-api	Scaled up replica set organisationValue-api-6f658cb5d5 to 5
2026-03-25T15:30:00.000Z	Normal	SuccessfulRescale	horizontalpodautoscaler/organisationValue-api	New size: 3; reason: All metrics below target
```

### Prometheus Metrics (Text Format)
```
# HELP container_cpu_usage_seconds_total Cumulative cpu time consumed by the container in seconds
# TYPE container_cpu_usage_seconds_total counter
container_cpu_usage_seconds_total{namespace="organisationValue",pod="organisationValue-api-6f658cb5d5-c9rxc",container="organisationValue-api"} 1234.567
container_cpu_usage_seconds_total{namespace="organisationValue",pod="organisationValue-api-6f658cb5d5-k7mnd",container="organisationValue-api"} 1189.234
container_cpu_usage_seconds_total{namespace="organisationValue",pod="organisationValue-api-6f658cb5d5-p2qrs",container="organisationValue-api"} 1256.789

# HELP container_memory_usage_bytes Current memory usage in bytes
# TYPE container_memory_usage_bytes gauge
container_memory_usage_bytes{namespace="organisationValue",pod="organisationValue-api-6f658cb5d5-c9rxc",container="organisationValue-api"} 1073741824
container_memory_usage_bytes{namespace="organisationValue",pod="organisationValue-api-6f658cb5d5-k7mnd",container="organisationValue-api"} 1342177280
container_memory_usage_bytes{namespace="organisationValue",pod="organisationValue-api-6f658cb5d5-p2qrs",container="organisationValue-api"} 1610612736

# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{namespace="organisationValue",service="organisationValue-api",method="GET",status="200"} 150234
http_requests_total{namespace="organisationValue",service="organisationValue-api",method="POST",status="201"} 23456
http_requests_total{namespace="organisationValue",service="organisationValue-api",method="GET",status="500"} 123
http_requests_total{namespace="organisationValue",service="organisationValue-api",method="POST",status="500"} 45

# HELP http_request_duration_seconds HTTP request latency histogram
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{namespace="organisationValue",service="organisationValue-api",le="0.01"} 50000
http_request_duration_seconds_bucket{namespace="organisationValue",service="organisationValue-api",le="0.05"} 120000
http_request_duration_seconds_bucket{namespace="organisationValue",service="organisationValue-api",le="0.1"} 145000
http_request_duration_seconds_bucket{namespace="organisationValue",service="organisationValue-api",le="0.5"} 165000
http_request_duration_seconds_bucket{namespace="organisationValue",service="organisationValue-api",le="1.0"} 170000
http_request_duration_seconds_bucket{namespace="organisationValue",service="organisationValue-api",le="+Inf"} 173690
http_request_duration_seconds_sum{namespace="organisationValue",service="organisationValue-api"} 8456.789
http_request_duration_seconds_count{namespace="organisationValue",service="organisationValue-api"} 173690
```

### kubectl top output
```
NAME                                    CPU(cores)   MEMORY(bytes)
organisationValue-api-6f658cb5d5-c9rxc            250m         1024Mi
organisationValue-api-6f658cb5d5-k7mnd            280m         1280Mi
organisationValue-api-6f658cb5d5-p2qrs            320m         1536Mi
organisationValue-db-0                            500m         2048Mi
organisationValue-redis-master-0                  100m         512Mi
organisationValue-nginx-ingress-controller-xyz    150m         256Mi
```

---

## 9. Incident Scenarios

### Scenario 1: CPU Spike (High Load)

**Timeline:**
```log
# 15:20:00 - Normal operation
2026-03-25T15:20:00.000Z	info	[organisationValue-api] CPU usage: 25%, Memory: 45%, Active connections: 150

# 15:21:00 - Traffic spike begins
2026-03-25T15:21:00.000Z	info	[nginx] Incoming request rate: 500 req/s (normal: 100 req/s)
2026-03-25T15:21:00.500Z	warn	[organisationValue-api] Thread pool saturation detected, queue depth: 200

# 15:21:30 - CPU spike
2026-03-25T15:21:30.000Z	warn	[kubernetes] CPU usage alert for pod organisationValue-api-6f658cb5d5-c9rxc: 85%
2026-03-25T15:21:30.100Z	Normal	SuccessfulRescale	horizontalpodautoscaler/organisationValue-api	New size: 8; reason: cpu resource utilization (percentage of request) above target

# 15:22:00 - CPU critical
2026-03-25T15:22:00.000Z	error	[organisationValue-api] Request timeout after 30s, correlationId: abc123
Mar 25, 2026 15:22:00:123 |organisationValue : ERROR |default-[pool-9-thread-1]: |abc12345-6789-0def-ghij-klmnopqrstuv| null:john.doe | tenantID:tenant-001: REQUEST_TIMEOUT cpu_throttling detected for project:proj-12345 username: john.doe organization: ACME-Corp

# 15:22:30 - New pods starting
2026-03-25T15:22:30.000Z	Normal	Scheduled	pod/organisationValue-api-6f658cb5d5-abc12	Successfully assigned organisationValue/organisationValue-api-6f658cb5d5-abc12 to node-worker-02
2026-03-25T15:22:35.000Z	Normal	Started	pod/organisationValue-api-6f658cb5d5-abc12	Started container organisationValue-api

# 15:23:00 - Load distribution improving
2026-03-25T15:23:00.000Z	info	[kubernetes] CPU usage normalized for pod organisationValue-api-6f658cb5d5-c9rxc: 45%
2026-03-25T15:23:00.500Z	info	[nginx] Request rate balanced across 8 pods

# 15:25:00 - Recovery
2026-03-25T15:25:00.000Z	info	[organisationValue-api] CPU usage: 30%, Memory: 50%, Active connections: 200
2026-03-25T15:25:00.500Z	info	[monitoring] Incident AUTO_RESOLVED: CPU_SPIKE duration: 5m
```

### Scenario 2: Memory Leak

**Timeline:**
```log
# Day 1 - 08:00 - Application starts fresh after deployment
2026-03-24T08:00:00.000Z	info	[organisationValue-api] Application started, heap: 256MB/2048MB (12.5%)
{"level":"info","time":"2026-03-24T08:00:00.000Z","msg":"JVM metrics","heapUsed":"256MB","heapMax":"2048MB","gcCount":0}

# Day 1 - 12:00 - Memory slowly increasing
2026-03-24T12:00:00.000Z	info	[organisationValue-api] Heap usage: 512MB/2048MB (25%)
{"level":"debug","time":"2026-03-24T12:00:00.000Z","msg":"GC stats","youngGC":{"count":150,"totalTime":"2.5s"},"oldGC":{"count":2,"totalTime":"500ms"}}

# Day 1 - 18:00 - Memory continues to grow
2026-03-24T18:00:00.000Z	info	[organisationValue-api] Heap usage: 896MB/2048MB (43.75%)

# Day 2 - 06:00 - Memory concerning
2026-03-25T06:00:00.000Z	warn	[organisationValue-api] Heap usage elevated: 1280MB/2048MB (62.5%)
Mar 25, 2026 06:00:00:123 |organisationValue : WARN |gc-[GC-thread-1]: |system| null:system | tenantID:null: MEMORY_WARNING heap_usage:62.5% gc_overhead:8% for project:system username: system organization: system

# Day 2 - 12:00 - Memory critical
2026-03-25T12:00:00.000Z	error	[organisationValue-api] MEMORY_CRITICAL heap_usage: 1792MB/2048MB (87.5%)
2026-03-25T12:00:00.500Z	warn	[kubernetes] Memory usage alert for pod organisationValue-api-6f658cb5d5-c9rxc: 87%
{"level":"error","time":"2026-03-25T12:00:00.000Z","msg":"GC overhead limit approaching","youngGC":{"count":5000,"totalTime":"250s"},"oldGC":{"count":45,"totalTime":"120s"},"gcOverhead":"18%"}

# Day 2 - 14:00 - Full GC cycles increasing
2026-03-25T14:00:00.000Z	error	[organisationValue-api] Frequent Full GC detected: 12 cycles in last hour
Mar 25, 2026 14:00:00:456 |organisationValue : ERROR |gc-[GC-thread-1]: |system| null:system | tenantID:null: GC_OVERHEAD_EXCEEDED gc_pause:15s heap_after_gc:1600MB for project:system username: system organization: system

# Day 2 - 15:00 - OOM approaching
2026-03-25T15:00:00.000Z	error	[organisationValue-api] OutOfMemoryError imminent, heap: 1950MB/2048MB (95.2%)
2026-03-25T15:00:01.000Z	Warning	OOMKilling	pod/organisationValue-api-6f658cb5d5-c9rxc	Memory usage exceeded limit
2026-03-25T15:00:01.500Z	Normal	Killing	pod/organisationValue-api-6f658cb5d5-c9rxc	Stopping container organisationValue-api

# Heap dump generated
Mar 25, 2026 15:00:00:789 |organisationValue : ERROR |default-[pool-9-thread-1]: |system| null:system | tenantID:null: HEAP_DUMP_GENERATED location:/tmp/heapdump-20260325-150000.hprof size:1.9GB for project:system username: system organization: system

# Pod restart
2026-03-25T15:00:02.000Z	Normal	Created	pod/organisationValue-api-6f658cb5d5-c9rxc	Created container organisationValue-api
2026-03-25T15:00:03.000Z	Normal	Started	pod/organisationValue-api-6f658cb5d5-c9rxc	Started container organisationValue-api
2026-03-25T15:00:03.500Z	info	[organisationValue-api] Application restarted, heap: 256MB/2048MB (12.5%)
```

### Scenario 3: Network Failure

**Timeline:**
```log
# 15:30:00 - Normal operation
2026-03-25T15:30:00.000Z	info	[istio] All upstream connections healthy
2026-03-25T15:30:00.000Z	info	[nginx] Upstream servers: 10.244.0.15:8080(up), 10.244.0.16:8080(up), 10.244.0.17:8080(up)

# 15:30:30 - Network partition begins (node-worker-02 isolated)
2026-03-25T15:30:30.000Z	error	[calico] Lost connectivity to node node-worker-02, BGP session down
2026-03-25T15:30:30.100Z	Warning	NodeNotReady	node/node-worker-02	Node node-worker-02 status is now: NodeNotReady

# 15:30:31 - Service discovery updates
2026-03-25T15:30:31.000Z	warn	[coredns] Removing endpoints for node-worker-02 pods
2026-03-25T15:30:31.500Z	warn	[istio] Endpoint 10.244.1.15:8080 marked unhealthy (no response)

# 15:30:32 - Connection failures begin
2026-03-25T15:30:32.000Z	error	[nginx] connect() failed (113: No route to host) while connecting to upstream, upstream: "http://10.244.1.15:8080"
Mar 25, 2026 15:30:32:123 |organisationValue : ERROR |default-[pool-9-thread-5]: |net12345-6789-0abc-defg-hijklmnopqrs| null:sarah.smith | tenantID:tenant-002: NETWORK_UNREACHABLE target:postgres-test.database.test.cluster.test for project:proj-67890 username: sarah.smith organization: TechStart
{"level":"error","time":"2026-03-25T15:30:32.000Z","correlationId":"net12345-6789-0abc-defg-hijklmnopqrs","msg":"Connection failed","error":"ENETUNREACH","target":"10.244.1.20:5432","retryCount":1}

# 15:30:35 - Circuit breaker triggers
2026-03-25T15:30:35.000Z	warn	[istio] Circuit breaker tripped for cluster outbound|5432||postgres-test.database.test.cluster.test
2026-03-25T15:30:35.500Z	warn	[organisationValue-api] Database connection pool exhausted, failover to replica initiated

# 15:30:40 - Failover in progress
2026-03-25T15:30:40.000Z	info	[organisationValue-api] Connecting to database replica: database-replica.database.svc.cluster.local
2026-03-25T15:30:41.000Z	info	[organisationValue-api] Database replica connection established (read-only mode)
Mar 25, 2026 15:30:41:456 |organisationValue : WARN |default-[pool-9-thread-1]: |sys00001-0000-0000-0000-000000000001| null:system | tenantID:null: DEGRADED_MODE write_operations_disabled for project:all username: system organization: system

# 15:31:00 - Kubernetes responds
2026-03-25T15:31:00.000Z	Normal	NodeNotReady	node/node-worker-02	Marking node as not ready
2026-03-25T15:31:00.500Z	Normal	TaintManagerEviction	pod/organisationValue-api-6f658cb5d5-abc12	Marking for deletion due to NoExecute taint
2026-03-25T15:31:01.000Z	Normal	SuccessfulCreate	replicaset/organisationValue-api-6f658cb5d5	Created pod: organisationValue-api-6f658cb5d5-new12

# 15:35:00 - Network recovered
2026-03-25T15:35:00.000Z	info	[calico] BGP session re-established with node-worker-02
2026-03-25T15:35:00.500Z	Normal	NodeReady	node/node-worker-02	Node node-worker-02 status is now: Ready
2026-03-25T15:35:01.000Z	info	[istio] Circuit breaker recovered for database-primary
2026-03-25T15:35:01.500Z	info	[organisationValue-api] Primary database connection restored, exiting read-only mode
```

### Scenario 4: Database Connection Pool Exhaustion

**Timeline:**
```log
# 15:40:00 - Normal operation
Mar 25, 2026 15:40:00:000 |organisationValue : INFO |default-[pool-9-thread-1]: |db-monitor| null:system | tenantID:null: CONNECTION_POOL_STATUS active:20/100 idle:80 for project:system username: system organization: system

# 15:41:00 - Slow queries begin (blocking connections)
Mar 25, 2026 15:41:00:123 |organisationValue : WARN |default-[pool-9-thread-10]: |slow12345-6789-0abc-defg-hijklmnopqrs| null:report.user | tenantID:tenant-001: SLOW_QUERY duration:45000ms query:SELECT_REPORT_DATA for project:proj-12345 username: report.user organization: ACME-Corp
2026-03-25 15:41:00,456 WARN  [org.hibernate.engine.jdbc.spi.SqlExceptionHelper] (default task-10) SQL Warning: Query execution exceeded 30s threshold

# 15:42:00 - Pool pressure increasing
Mar 25, 2026 15:42:00:000 |organisationValue : WARN |default-[pool-9-thread-1]: |db-monitor| null:system | tenantID:null: CONNECTION_POOL_WARNING active:75/100 idle:25 wait_queue:15 for project:system username: system organization: system
25-Mar-2026 15:42:00.123 WARNING [http-nio-8080-Acceptor] org.apache.tomcat.util.threads.LimitLatch.await Connection limit reached, connections waiting: 25

# 15:43:00 - Pool near exhaustion
Mar 25, 2026 15:43:00:000 |organisationValue : ERROR |default-[pool-9-thread-1]: |db-monitor| null:system | tenantID:null: CONNECTION_POOL_CRITICAL active:95/100 idle:5 wait_queue:50 avg_wait:5000ms for project:system username: system organization: system
2026-03-25 15:43:00,234 WARN  [org.jboss.jca.adapters.jdbc.local.LocalManagedConnectionFactory] (JCA PoolFiller) IJ000604: Pool near exhaustion, available: 5/100

# 15:43:30 - Timeouts begin
Mar 25, 2026 15:43:30:456 |organisationValue : ERROR |default-[pool-9-thread-15]: |conn12345-6789-0abc-defg-hijklmnop123| null:john.doe | tenantID:tenant-001: CONNECTION_TIMEOUT waited:30000ms for project:proj-12345 username: john.doe organization: ACME-Corp
{"level":"error","time":"2026-03-25T15:43:30.456Z","correlationId":"conn12345-6789-0abc-defg-hijklmnop123","msg":"Failed to acquire database connection","error":"ConnectionPoolTimeoutException","waitTime":"30000ms","poolStatus":{"active":100,"idle":0,"waiting":75}}

# 15:44:00 - Pool completely exhausted
Mar 25, 2026 15:44:00:000 |organisationValue : ERROR |default-[pool-9-thread-1]: |db-monitor| null:system | tenantID:null: CONNECTION_POOL_EXHAUSTED active:100/100 idle:0 wait_queue:100 rejecting_connections:true for project:system username: system organization: system
2026-03-25 15:44:00,789 ERROR [org.jboss.jca.core.connectionmanager.pool.strategy.OnePool] (default task-50) IJ000453: Unable to get managed connection for java:jboss/datasources/organisationValueDS

# 15:44:30 - Emergency action: killing long-running queries
Mar 25, 2026 15:44:30:123 |organisationValue : WARN |admin-[pool-1-thread-1]: |admin-001| null:admin | tenantID:null: KILLING_LONG_QUERIES threshold:60s count:5 for project:system username: admin organization: system

# 15:45:00 - Recovery begins
Mar 25, 2026 15:45:00:000 |organisationValue : INFO |default-[pool-9-thread-1]: |db-monitor| null:system | tenantID:null: CONNECTION_POOL_RECOVERING active:60/100 idle:40 wait_queue:20 for project:system username: system organization: system

# 15:46:00 - Normal operation restored
Mar 25, 2026 15:46:00:000 |organisationValue : INFO |default-[pool-9-thread-1]: |db-monitor| null:system | tenantID:null: CONNECTION_POOL_NORMAL active:25/100 idle:75 wait_queue:0 for project:system username: system organization: system
```

### Scenario 5: Disk Space Exhaustion

**Timeline:**
```log
# 15:50:00 - Warning threshold reached
2026-03-25T15:50:00.000Z	Warning	FreeDiskSpaceLow	node/node-worker-01	Available bytes 10737418240 is less than 10% of capacity 107374182400
{"level":"warn","time":"2026-03-25T15:50:00.000Z","msg":"Disk space warning","mount":"/var/lib/containers","available":"10GB","total":"100GB","percentUsed":"90%"}

# 15:55:00 - Critical threshold
2026-03-25T15:55:00.000Z	Warning	FreeDiskSpaceCritical	node/node-worker-01	Available bytes 5368709120 is less than 5% of capacity 107374182400
Mar 25, 2026 15:55:00:123 |organisationValue : ERROR |async-[pool-12-thread-1]: |disk-monitor| null:system | tenantID:null: DISK_SPACE_CRITICAL mount:/var/lib/containers available:5GB threshold:5% for project:system username: system organization: system

# 15:55:30 - Log writes failing
2026-03-25 15:55:30,456 ERROR [org.jboss.logmanager] Failed to write to log file: No space left on device
{"level":"error","time":"2026-03-25T15:55:30.000Z","msg":"Failed to write audit log","error":"ENOSPC: no space left on device"}

# 15:56:00 - Pod eviction begins
2026-03-25T15:56:00.000Z	Warning	Evicted	pod/organisationValue-api-6f658cb5d5-c9rxc	The node had condition: [DiskPressure]
2026-03-25T15:56:00.500Z	Normal	Killing	pod/organisationValue-api-6f658cb5d5-c9rxc	Stopping container organisationValue-api due to eviction

# 15:56:30 - Emergency cleanup triggered
2026-03-25T15:56:30.000Z	info	[kubelet] Starting garbage collection: removing unused images
2026-03-25T15:56:35.000Z	info	[kubelet] Removed image registry.acme-corp.com/old-api:v2.3.0, freed 1.5GB
2026-03-25T15:56:40.000Z	info	[kubelet] Removed image registry.acme-corp.com/old-api:v2.4.0, freed 1.5GB

# 15:57:00 - Log rotation triggered
Mar 25, 2026 15:57:00:000 |organisationValue : INFO |async-[pool-12-thread-1]: |disk-monitor| null:system | tenantID:null: LOG_ROTATION_TRIGGERED freed:8GB files_rotated:25 for project:system username: system organization: system

# 15:58:00 - Recovery
2026-03-25T15:58:00.000Z	info	[kubelet] DiskPressure condition cleared, available: 25GB
2026-03-25T15:58:00.500Z	Normal	NodeHasSufficientDisk	node/node-worker-01	Node node-worker-01 status is now: NodeHasSufficientDisk
```

### Scenario 6: SSL/TLS Certificate Expiry

**Timeline:**
```log
# 7 days before expiry
2026-03-18T00:00:00.000Z	warn	[cert-manager] Certificate organisationValue-tls will expire in 7 days
Mar 18, 2026 00:00:00:000 |organisationValue : WARN |scheduler-[pool-1-thread-1]: |cert-check| null:system | tenantID:null: CERTIFICATE_EXPIRY_WARNING cert:organisationValue-tls expires_in:7d for project:system username: system organization: system

# 1 day before expiry
2026-03-24T00:00:00.000Z	error	[cert-manager] URGENT: Certificate organisationValue-tls will expire in 1 day
2026/03/24 00:00:00 [warn] 12345#12345: SSL certificate for "organisationValue.acme-corp.com" expires in 1 day

# Certificate expired
2026-03-25T00:00:00.000Z	error	[cert-manager] Certificate organisationValue-tls has EXPIRED
2026/03/25 00:00:01 [error] 12345#12345: SSL certificate verify error (10: certificate has expired) for "organisationValue.acme-corp.com"

# Client connection failures
2026/03/25 15:00:00 [error] 12345#12345: *12345 SSL_do_handshake() failed (SSL: error:0A000086:SSL routines::certificate verify failed), client: 192.168.1.50
{"level":"error","time":"2026-03-25T15:00:00.000Z","msg":"TLS handshake failed","error":"certificate has expired","client":"192.168.1.50","serverName":"organisationValue.acme-corp.com"}

# Emergency certificate renewal
2026-03-25T15:01:00.000Z	info	[cert-manager] Initiating emergency certificate renewal for organisationValue-tls
2026-03-25T15:01:30.000Z	info	[cert-manager] Certificate renewed successfully, new expiry: 2026-06-25
2026-03-25T15:01:31.000Z	info	[nginx] Reloading configuration with new certificate
2026/03/25 15:01:31 [notice] 12345#12345: signal 1 (SIGHUP) received from 1, reconfiguring
2026/03/25 15:01:32 [notice] 12345#12345: using new certificate for "organisationValue.acme-corp.com"
```

---

## Appendix A: Log Level Reference

| Level | Description | Action Required |
|-------|-------------|-----------------|
| TRACE | Detailed debugging information | None (development only) |
| DEBUG | Diagnostic information | None (troubleshooting) |
| INFO | Normal operational messages | None |
| WARN | Potential issues that may need attention | Review within 24 hours |
| ERROR | Errors that affect specific operations | Investigate immediately |
| FATAL/CRITICAL | System-wide failures | Emergency response |

## Appendix B: Common Correlation ID Patterns

| Pattern | Source | Example |
|---------|--------|---------|
| UUID v4 | Application generated | `f03dfc7d-8686-4681-a33e-9146e7a7d3b0` |
| X-Request-ID | HTTP headers | `req-20260325-150316-abc123` |
| Trace ID | OpenTelemetry/Jaeger | `4bf92f3577b34da6a3ce929d0e0e4736` |
| Span ID | OpenTelemetry/Jaeger | `00f067aa0ba902b7` |

## Appendix C: Quick Reference - Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `CONNECTION_TIMEOUT` | Database/service unreachable | Network issues, service down |
| `POOL_EXHAUSTED` | No available connections | Slow queries, connection leaks |
| `OOM_KILLED` | Out of memory | Memory leak, insufficient resources |
| `ENOSPC` | Disk full | Log accumulation, large uploads |
| `ENETUNREACH` | Network unreachable | Network partition, firewall |
| `CERT_EXPIRED` | TLS certificate expired | Certificate not renewed |

---
