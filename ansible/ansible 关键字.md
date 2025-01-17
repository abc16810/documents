- **become** 布尔值，控制在任务执行中是否使用特权升级

  ```
  # 由become插件实现, 在hosts文件中group中进行设置
  [test] 
  ansible_become=true 
  ansible_become_method=sudo 
  ansible_become_user=root 
  ansible_become_pass=xxx
  # 在playbook 或者tasks中设置
  - hosts: localhost
    user: test
    become: true
    become_user: root
    roles:
      - role: "init_hosts"
  ```

- **check_mode ** 布尔值，用于控制任务是否在' check '模式下执行,,就是一种假装对系统做修改但是实际上并没有改变系统的一种操作模式

  ```
  - name: 检查是否安装了NGINX  # 如果变量install为changed的说明没有安装nginx
    package:
       name: nginx
       state: present
    check_mode: true
  ```
  
- **collections**用于搜索模块、插件的集合命名空间列表

- **connection**  更改要在目标机器上执行的任务连接插件  默认ssh

- **debugger ** 根据任务结果的状态打开调试任务

  ```
  - name: 执行命令   
    command: lss /tmp
    debugger: on_failed   # 如果任务失败，Ansible将调用调试器
  ```

- **diff**  任务执行后结果是否返回与之前相比较' diff '

- **environment**  字典，它被转换成环境变量，在执行时提供给任务。这只能与模块一起使用

- **gather_facts ** 布尔值，是否收集主机信息

- **handlers**  后续处理程序

- **hosts**  指定执行任务主机/主机组，all 表示所有

- **ignore_errors**  布尔值，忽略任务失败并继续play

- **ignore_unreachable** 布尔值，忽略由于主机不可达而导致的任务失败，并继续play

- **name**  标识符，描述性信息，可以用于文档，也可以用于任务/处理程序

- **port**   用于覆盖连接中使用的默认端口

- **post_tasks**  在所有tasks部分之后要执行的任务列表

  ```
  roles:
      - role: "mysql_install"
   post_tasks:
       - name: 确保mysql 启动
         service:
           name: mysqld
           state: started
  ```

- **pre_tasks** 在执行roles之前执行的任务列表

  ```
    ...
    pre_tasks:
       - name: 检查支持的操作系统
         assert:
           that:
             - (ansible_os_family == 'RedHat' and ansible_distribution_major_version == '7')
           msg: "仅支持(redhat) CentOS 7 (WIP)"
    roles:
      - role: "init_hosts"
        tags:
          - init
  ```

- **roles**   指定要运行角色列表

  ```
  roles:
    - role: "init_hosts"
  ```

- **remote_user**  在目标机器上执行的用户

  ```
  remote_user: root
  ```

- **run_once** 布尔值，它将绕过主机循环，任务尝试在第一个可用的主机上执行，然后将所有结果应用到同一批中的所有活动主机

  ```
  - name: 本地生成主机文件hosts的模板脚本应用于所有执行play的主机
    template:
      src: "set-host-hostfile-setup.sh.j2"
      dest: "/var/tmp/set-host-hostfile-setup.sh"
      mode: "0755"
    run_once: true
  ```

- **serial**一次批量执行多少个主机，对于滚动更新很有用

  ```
  # 如果我们在“webservers”组中有6台主机，Ansible将在其中3台主机上执行完整的play(两个任务)，然后再转向下3台主机:
  - name: test play
    hosts: webservers
    serial: 3
    tasks:
      - name: first task
        command: hostname
      - name: second task
        command: hostname
  ```

- **tags**  定义任务标签

  ```
    ...
    tags:
      - always
    tags:
      - set-hosts
  # ansible-playbook -t 指定上述tag标签  来运行指定的tag任务 always标签一直运行
  ```

- **tasks** 剧中要执行的主要任务列表

- **vars**  指定变量列表

  ```
  vars:
    - foo: bar
  ```

- **vars_files**  指定变量文件

  ```
  vars_files:
      - default_vars.yml
  ```

- **timeout**  连接超时单位秒

- **delegate_to** 委派任务到其他机器上运行

- **when** 条件表达式，用于确定是否运行任务的迭代

  ```
  when: ansible_os_family == 'RedHat'  # 判断变量
  when:
      - set_hosts | bool    # 布尔值判断
  when: result|failed  第一条命令失败时（result 为failed时），才执行
  when: result|success  （result 为success时），才执行
  when: result|skipped 
  when: inventory_hostname in groups['master']  # 包含
   when:
       - foo is defined  # 判断变量是否定义
  ```

- **block**  定义一个块中的任务列表  可以嵌套

  ```
  - name: (RHEL 8) Setup Python 3
    block:
          - name: (RHEL 8) Install Python 3
            yum:
              name:
                - python3
                - python3-pip
                - python3-devel
              update_cache: true
          - name: (RHEL 8) Set Python 3 as default
            alternatives:
              name: python
              path: /usr/bin/python3
              link: /usr/bin/python
    when:
          - ansible_facts['os_family'] == "RedHat"
          - ansible_facts['distribution_major_version'] is version('8', '==')
  ```

- **args** 向任务中添加参数的第二种方法。获取一个字典，其中的键映射到选项和值。.

  ```
  shell: xxx
   args:
     warn: no
  # 这样终端输出没有警告 详情ansible-doc shell 
  ```

- **async**  如果C(action)支持此操作，则异步运行任务,value是最大运行时(以秒为单位)

- **poll **设置异步任务的轮询间隔(默认为10秒)

  默认情况下，Ansible同步运行任务，保持到远程节点的连接打开，直到操作完成。这意味着在剧本中，每个任务默认阻塞下一个任务，这意味着在当前任务完成之前，后续任务将不会运行。这种行为会带来挑战。例如，任务的完成时间可能比SSH会话允许的时间长，从而导致超时。或者，当您同时执行其他任务时，您可能希望一个长时间运行的进程在后台执行。异步模式允许您控制长时间运行的任务的执行方式

  `poll>0`如果您希望在剧本中为某个任务设置更长的超时限制，请使用将async与poll设置为正值的方法。Ansible仍然会阻塞你剧本中的下一个任务，等待直到异步任务完成，失败或超时。但是，任务只有在超过使用async参数设置的超时限制时才会超时。

  ```
    - name: Simulate long running op (15 sec), wait for up to 45 sec, poll every 5 sec
      ansible.builtin.command: /bin/sleep 15
      async: 45  
      poll: 5
  ```

  如果您希望在剧本中同时运行多个任务，请使用async并将poll设置为0。当你设置poll: 0时，Ansible会启动任务并立即开始下一个任务，而不需要等待结果。每个异步任务运行到完成、失败或超时(运行时间超过其异步值)。剧本运行结束时不检查异步任务
  
  ```
    - name: Simulate long running op, allow to run for 45 sec, fire and forget
      ansible.builtin.command: /bin/sleep 15
      async: 45
      poll: 0
  ```
  
- **register**   注册模块运行后的状态和数据

- **until**    和retries，delay 组合使用，直到满足这里提供的条件或达到retries限制

- **retries**  和until ， delay 组合使用， 在until循环中重试次数

- **delay**   重试之间的延迟秒数。此设置仅与until组合使用

  ```
  - name: 禁用postfix服务
    service:
      name: postfix
      enabled: no
      state: "stopped"
    failed_when: false
    register: _stop
    until: _stop is success
    retries: 5
    delay: 2
  ```

- **changed_when**   通过条件表达式 覆盖任务的正常“更改”状态

- **failed_when**    通过条件表达式，覆盖任务的正常“失败”状态

  ```
  - name: 运行 authorized keys 脚本文件
    command: "/var/tmp/ssh-key.sh"
    register: key_create
    changed_when: key_create.rc == 3   # 当 条件为true，任务为changed状态
    failed_when:
      - key_create.rc != 3
      - key_create.rc != 0
  ```

- **notify**  当任务返回' changed=True '状态时要通知的处理程序列表

  ```
  - name: 禁用Selinux
    selinux:
      state: disabled
    notify:     # 如果成功修改了selinux为dis状态，则通知处理程序重启系统
       - reboot system 
  ```

- **local_action**    与action相同，但也意味着delegate_to: localhost

- **loop** 获取要迭代的任务的列表，将每个列表元素保存到item变量中(可通过loop_control进行配置)

  ```
      - name: loop
        debug:
           msg: "{{ item }}"
        loop: [1,2,3,4,5]
  ```

  