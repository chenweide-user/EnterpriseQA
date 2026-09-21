-- ==========================================================================
-- RAG 企业内部知识库问答系统 - 建库建表脚本 + 测试数据
-- MySQL 8.0.46 / 端口 3308
-- 字符集：utf8mb4
-- 说明：所有测试账号的密码均为 123456（MD5 值：e10adc3949ba59abbe56e057f20f883e）
-- ==========================================================================

-- --------------------------------------------------------------------------
-- 一、创建数据库
-- --------------------------------------------------------------------------
DROP DATABASE IF EXISTS db_enterprise_qa;
CREATE DATABASE db_enterprise_qa
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;
USE db_enterprise_qa;

-- --------------------------------------------------------------------------
-- 二、用户表 sys_user
-- --------------------------------------------------------------------------
DROP TABLE IF EXISTS sys_user;
CREATE TABLE sys_user (
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键',
    username    VARCHAR(50)  NOT NULL                COMMENT '登录用户名，唯一',
    password    VARCHAR(64)  NOT NULL                COMMENT '登录密码，MD5加密存储',
    real_name   VARCHAR(50)  DEFAULT NULL            COMMENT '真实姓名',
    email       VARCHAR(100) DEFAULT NULL            COMMENT '邮箱地址（唯一）',
    phone       VARCHAR(20)  DEFAULT NULL            COMMENT '手机号码（唯一）',
    role        VARCHAR(20)  NOT NULL DEFAULT 'user' COMMENT '角色：admin-管理员，user-普通用户',
    status      TINYINT      NOT NULL DEFAULT 1      COMMENT '账号状态：1-启用，0-禁用',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    UNIQUE KEY uk_phone (phone)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '系统用户表';

-- --------------------------------------------------------------------------
-- 三、知识库表 knowledge_base
-- --------------------------------------------------------------------------
DROP TABLE IF EXISTS knowledge_base;
CREATE TABLE knowledge_base (
    id              BIGINT       NOT NULL AUTO_INCREMENT COMMENT '知识库ID，主键',
    name            VARCHAR(100) NOT NULL                COMMENT '知识库名称，唯一',
    description     TEXT         DEFAULT NULL            COMMENT '知识库描述',
    collection_name VARCHAR(100) NOT NULL                COMMENT 'Chroma向量库集合名称',
    user_id         BIGINT       NOT NULL                COMMENT '创建人ID，关联sys_user.id',
    doc_count       INT          NOT NULL DEFAULT 0       COMMENT '知识库下的文档数量',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_name (name),
    UNIQUE KEY uk_collection_name (collection_name),
    KEY idx_user_id (user_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '知识库表';

-- --------------------------------------------------------------------------
-- 四、文档表 document
-- --------------------------------------------------------------------------
DROP TABLE IF EXISTS document;
CREATE TABLE document (
    id           BIGINT      NOT NULL AUTO_INCREMENT COMMENT '文档ID，主键',
    kb_id        BIGINT      NOT NULL                COMMENT '所属知识库ID，关联knowledge_base.id',
    file_name    VARCHAR(255) NOT NULL               COMMENT '原始文件名',
    file_path    VARCHAR(500) NOT NULL               COMMENT '文件在服务器上的存储路径',
    file_type    VARCHAR(20)  NOT NULL               COMMENT '文件类型（后缀），如 pdf/docx/txt/md',
    file_size    BIGINT       NOT NULL DEFAULT 0     COMMENT '文件大小，单位字节',
    chunk_count  INT          NOT NULL DEFAULT 0     COMMENT '文档切片数量',
    status       VARCHAR(20)  NOT NULL DEFAULT 'processing' COMMENT '处理状态：processing-处理中，completed-已完成，failed-失败',
    error_msg    VARCHAR(500) DEFAULT NULL           COMMENT '处理失败时的错误信息',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    PRIMARY KEY (id),
    KEY idx_kb_id (kb_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '文档表';

-- --------------------------------------------------------------------------
-- 五、问答会话表 chat_session
-- --------------------------------------------------------------------------
DROP TABLE IF EXISTS chat_session;
CREATE TABLE chat_session (
    id         BIGINT      NOT NULL AUTO_INCREMENT COMMENT '会话ID，主键',
    user_id    BIGINT      NOT NULL                COMMENT '提问用户ID，关联sys_user.id',
    kb_id      BIGINT      NOT NULL                COMMENT '提问时选择的知识库ID',
    title      VARCHAR(200) NOT NULL               COMMENT '会话标题，默认取首个问题前20字',
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_kb_id (kb_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '问答会话表';

-- --------------------------------------------------------------------------
-- 六、对话消息表 chat_message
-- --------------------------------------------------------------------------
DROP TABLE IF EXISTS chat_message;
CREATE TABLE chat_message (
    id         BIGINT   NOT NULL AUTO_INCREMENT COMMENT '消息ID，主键',
    session_id BIGINT   NOT NULL                COMMENT '所属会话ID，关联chat_session.id',
    role       VARCHAR(20) NOT NULL             COMMENT '消息角色：user-用户提问，assistant-AI回答',
    content    TEXT     NOT NULL                COMMENT '消息内容',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '消息时间',
    PRIMARY KEY (id),
    KEY idx_session_id (session_id),
    KEY idx_role_created (role, created_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '对话消息表';

-- ==========================================================================
-- 测试数据
-- ==========================================================================

-- --------------------------------------------------------------------------
-- 用户数据（密码均为 123456）
-- --------------------------------------------------------------------------
INSERT INTO sys_user (id, username, password, real_name, email, phone, role, status) VALUES
(1, 'admin',    'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'admin@company.com',    '13800000001', 'admin', 1),
(2, 'zhangsan', 'e10adc3949ba59abbe56e057f20f883e', '张三',       'zhangsan@company.com', '13800000002', 'user',  1),
(3, 'lisi',     'e10adc3949ba59abbe56e057f20f883e', '李四',       'lisi@company.com',     '13800000003', 'user',  1),
(4, 'wangwu',   'e10adc3949ba59abbe56e057f20f883e', '王五',       'wangwu@company.com',   '13800000004', 'user',  0);

-- --------------------------------------------------------------------------
-- 知识库数据
-- --------------------------------------------------------------------------
INSERT INTO knowledge_base (id, name, description, collection_name, user_id, doc_count) VALUES
(1, '人事制度库', '存放公司考勤、休假、招聘等人力资源相关制度文档', 'kb_hr',      1, 2),
(2, '财务制度库', '存放差旅报销、费用管理、预算制度等财务相关文档', 'kb_finance', 1, 2),
(3, '产品技术库', '存放产品需求、技术架构、接口说明等研发相关文档', 'kb_product', 1, 2);

-- --------------------------------------------------------------------------
-- 文档数据（注意：此处仅为业务记录，向量数据需通过"文档管理"页面上传后生成）
-- --------------------------------------------------------------------------
INSERT INTO document (id, kb_id, file_name, file_path, file_type, file_size, chunk_count, status) VALUES
(1, 1, '员工考勤管理制度.pdf',   'uploads/员工考勤管理制度.pdf',   'pdf',  256000, 8,  'completed'),
(2, 1, '员工休假管理办法.docx',  'uploads/员工休假管理办法.docx',  'docx', 128000, 6,  'completed'),
(3, 2, '差旅费报销管理规定.pdf', 'uploads/差旅费报销管理规定.pdf', 'pdf',  312000, 10, 'completed'),
(4, 2, '费用报销操作手册.docx',  'uploads/费用报销操作手册.docx',  'docx', 168000, 7,  'completed'),
(5, 3, '产品需求文档V2.0.pdf',   'uploads/产品需求文档V2.0.pdf',   'pdf',  480000, 15, 'completed'),
(6, 3, '技术架构设计说明书.docx','uploads/技术架构设计说明书.docx','docx', 220000, 9,  'completed');

-- --------------------------------------------------------------------------
-- 问答会话数据
-- --------------------------------------------------------------------------
INSERT INTO chat_session (id, user_id, kb_id, title, created_at) VALUES
(1, 2, 1, '年假天数怎么计算？',           DATE_SUB(NOW(), INTERVAL 6 DAY)),
(2, 3, 2, '差旅费报销需要什么材料？',     DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 2, 3, '系统技术架构是怎样的？',       DATE_SUB(NOW(), INTERVAL 4 DAY)),
(4, 4, 1, '迟到会扣工资吗？',             DATE_SUB(NOW(), INTERVAL 3 DAY)),
(5, 3, 2, '费用报销审批流程？',           DATE_SUB(NOW(), INTERVAL 2 DAY)),
(6, 2, 1, '试用期有多久？',               DATE_SUB(NOW(), INTERVAL 1 DAY)),
(7, 3, 3, '产品V2.0有哪些新功能？',       DATE_SUB(NOW(), INTERVAL 0 DAY));

-- --------------------------------------------------------------------------
-- 对话消息数据（覆盖近 7 天，保证"提问趋势图"每天都有数据）
-- --------------------------------------------------------------------------
-- 第 -6 天（3 个提问）
INSERT INTO chat_message (session_id, role, content, created_at) VALUES
(1, 'user',      '年假天数怎么计算？',                       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 6 DAY), '09:10:00')),
(1, 'assistant', '入职满一年可享受5天带薪年假，每增加一年递增1天。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 6 DAY), '09:10:05')),
(1, 'user',      '年假可以跨年使用吗？',                     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 6 DAY), '09:15:00')),
(1, 'assistant', '年假原则上当年使用，特殊情况经审批可延至次年一季度。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 6 DAY), '09:15:06')),
(1, 'user',      '病假需要提供什么证明？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 6 DAY), '10:02:00')),
(1, 'assistant', '请提供二级以上医院开具的病假证明。',       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 6 DAY), '10:02:04'));

-- 第 -5 天（5 个提问）
INSERT INTO chat_message (session_id, role, content, created_at) VALUES
(2, 'user',      '差旅费报销需要什么材料？',                 TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '09:30:00')),
(2, 'assistant', '需要发票、行程单和审批通过的OA申请单。',  TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '09:30:05')),
(2, 'user',      '住宿报销标准是多少？',                     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '09:35:00')),
(2, 'assistant', '一线城市每晚不超过500元，其他城市不超过350元。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '09:35:06')),
(2, 'user',      '交通费用都可以报销吗？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '14:00:00')),
(2, 'assistant', '高铁二等座、飞机经济舱可按标准报销。',     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '14:00:05')),
(2, 'user',      '报销多久能到账？',                         TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '14:20:00')),
(2, 'assistant', '财务复核通过后5个工作日内付款。',         TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '14:20:05')),
(2, 'user',      '电子发票可以报销吗？',                     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '16:10:00')),
(2, 'assistant', '真实有效的电子发票与纸质发票具有同等效力。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 5 DAY), '16:10:05'));

-- 第 -4 天（2 个提问）
INSERT INTO chat_message (session_id, role, content, created_at) VALUES
(3, 'user',      '系统技术架构是怎样的？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 4 DAY), '11:00:00')),
(3, 'assistant', '系统采用前后端分离架构，后端FastAPI，前端Vue3。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 4 DAY), '11:00:06')),
(3, 'user',      '向量数据库用的是什么？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 4 DAY), '11:10:00')),
(3, 'assistant', '向量检索使用Chroma数据库，支持本地持久化。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 4 DAY), '11:10:05'));

-- 第 -3 天（6 个提问）
INSERT INTO chat_message (session_id, role, content, created_at) VALUES
(4, 'user',      '迟到会扣工资吗？',                         TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:40:00')),
(4, 'assistant', '每月迟到前两次不扣薪，第三次起按分钟计扣。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:40:05')),
(4, 'user',      '忘记打卡怎么办？',                         TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:45:00')),
(4, 'assistant', '可在OA系统提交补卡申请，由直属上级审批。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:45:06')),
(4, 'user',      '加班可以调休吗？',                         TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '13:00:00')),
(4, 'assistant', '工作日加班按1:1折算调休，需在3个月内使用。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '13:00:05')),
(4, 'user',      '调休需要提前申请吗？',                     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '13:10:00')),
(4, 'assistant', '调休1天以内提前1天申请，3天以内提前3天申请。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '13:10:05')),
(4, 'user',      '考勤记录在哪里查询？',                     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '15:00:00')),
(4, 'assistant', '可登录OA系统在考勤模块查询个人考勤明细。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '15:00:04')),
(4, 'user',      '全勤奖有什么条件？',                       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '17:30:00')),
(4, 'assistant', '当月无迟到、早退、旷工记录即可享受全勤奖。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 DAY), '17:30:05'));

-- 第 -2 天（4 个提问）
INSERT INTO chat_message (session_id, role, content, created_at) VALUES
(5, 'user',      '费用报销审批流程？',                       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '09:00:00')),
(5, 'assistant', '先在OA提交申请，经部门经理和财务依次审批。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '09:00:06')),
(5, 'user',      '超过多少需要总经理审批？',                 TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '09:20:00')),
(5, 'assistant', '单笔报销金额超过5000元需总经理审批。',     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '09:20:05')),
(5, 'user',      '招待费报销有什么要求？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '10:30:00')),
(5, 'assistant', '需附招待事由、人员名单和正规发票。',       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '10:30:04')),
(5, 'user',      '发票抬头开错了怎么办？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '15:40:00')),
(5, 'assistant', '请联系开票方作废原发票并重新开具。',       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 2 DAY), '15:40:05'));

-- 第 -1 天（7 个提问）
INSERT INTO chat_message (session_id, role, content, created_at) VALUES
(6, 'user',      '试用期有多久？',                           TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '09:05:00')),
(6, 'assistant', '劳动合同期限三年，试用期为三个月。',       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '09:05:05')),
(6, 'user',      '试用期工资怎么算？',                       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '09:15:00')),
(6, 'assistant', '试用期工资不低于转正工资的80%。',          TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '09:15:05')),
(6, 'user',      '试用期可以请假吗？',                       TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '10:00:00')),
(6, 'assistant', '试用期可以请假，但请假天数不计入试用期考察。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '10:00:06')),
(6, 'user',      '转正需要满足什么条件？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '11:00:00')),
(6, 'assistant', '通过试用期考核且无重大违纪即可按期转正。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '11:00:05')),
(6, 'user',      '入职需要准备哪些材料？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '14:00:00')),
(6, 'assistant', '需准备身份证、学历证明、离职证明和银行卡复印件。', TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '14:00:06')),
(6, 'user',      '五险一金什么时候开始缴纳？',               TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '15:00:00')),
(6, 'assistant', '自入职当月起依法缴纳五险一金。',           TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '15:00:04')),
(6, 'user',      '试用期可以提前转正吗？',                   TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '16:30:00')),
(6, 'assistant', '表现特别优异者经部门申请可提前转正。',     TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '16:30:05'));

-- 今天（5 个提问，"今日提问数"由此统计）
INSERT INTO chat_message (session_id, role, content, created_at) VALUES
(7, 'user',      '产品V2.0有哪些新功能？',                   TIMESTAMP(CURDATE(), '09:00:00')),
(7, 'assistant', 'V2.0新增了智能搜索、数据看板和消息推送功能。', TIMESTAMP(CURDATE(), '09:00:06')),
(7, 'user',      '智能搜索支持哪些内容？',                   TIMESTAMP(CURDATE(), '09:10:00')),
(7, 'assistant', '支持对文档标题和正文内容进行全文语义检索。', TIMESTAMP(CURDATE(), '09:10:05')),
(7, 'user',      '数据看板可以导出吗？',                     TIMESTAMP(CURDATE(), '10:00:00')),
(7, 'assistant', '数据看板支持导出为Excel和PDF格式。',       TIMESTAMP(CURDATE(), '10:00:04')),
(7, 'user',      'V2.0支持移动端吗？',                       TIMESTAMP(CURDATE(), '10:30:00')),
(7, 'assistant', 'V2.0已完成移动端适配，支持手机浏览器访问。', TIMESTAMP(CURDATE(), '10:30:05')),
(7, 'user',      '消息推送怎么设置？',                       TIMESTAMP(CURDATE(), '11:00:00')),
(7, 'assistant', '可在个人设置中开启系统通知和邮件提醒。',   TIMESTAMP(CURDATE(), '11:00:05'));

-- --------------------------------------------------------------------------
-- 自增起始值说明：
-- 种子数据使用显式ID插入，MySQL 会自动将 AUTO_INCREMENT 设为 MAX(id)+1，
-- 后续新增记录会从种子数据末尾连续递增，无需人为抬高起始值，避免产生ID断层。
-- 如需调整起始值，请使用：ALTER TABLE <表名> AUTO_INCREMENT = <目标值>;
-- --------------------------------------------------------------------------
