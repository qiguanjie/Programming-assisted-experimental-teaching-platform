create table userInformation
(
    email           varchar(45)   not null,
    password        varchar(128)  null,
    phone           varchar(45)   null,
    nickname        varchar(45)   null,
    usertype        int default 0 null,
    creat_time_user datetime      null,
    constraint userInformation_email_uindex
        unique (email)
);

create table formula_post
(
    formula_id int                                        not null,
    author     varchar(128)                               not null,
    title      varchar(256) default '空标题'                 null,
    creat_time datetime     default '2000-09-09 09:09:09' null,
    constraint formula_post_formula_id_uindex
        unique (formula_id),
    constraint formula_post_userInformation_email_fk
        foreign key (author) references userInformation (email)
);

alter table formula_post
    add primary key (formula_id);

create table question_detail
(
    formula_id int         not null,
    qno        int         not null,
    content    text        null,
    datetime   datetime    null,
    author     varchar(45) null,
    primary key (formula_id, qno),
    constraint question_detail_formula_post_formula_id_fk
        foreign key (formula_id) references formula_post (formula_id),
    constraint question_detail_userInformation_email_fk
        foreign key (author) references userInformation (email)
);


