--
-- PostgreSQL database dump
--

\restrict LUCVenvlXW37VAYH0qSccbqoXHFcdxtPZ7uzOmTMyo780HX5UofA8xs2V8rreeC

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-12-02 22:59:50

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 24641)
-- Name: appointment_statuses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.appointment_statuses (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(255)
);


ALTER TABLE public.appointment_statuses OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24640)
-- Name: appointment_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.appointment_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.appointment_statuses_id_seq OWNER TO postgres;

--
-- TOC entry 4922 (class 0 OID 0)
-- Dependencies: 221
-- Name: appointment_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.appointment_statuses_id_seq OWNED BY public.appointment_statuses.id;


--
-- TOC entry 226 (class 1259 OID 24660)
-- Name: appointments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.appointments (
    id integer NOT NULL,
    client_id integer,
    employee_id integer,
    clinic_id integer DEFAULT 1 NOT NULL,
    status_id integer,
    service_id integer,
    appointment_date date NOT NULL,
    appointment_time time without time zone NOT NULL,
    duration_minutes integer NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    price numeric(10,2)
);


ALTER TABLE public.appointments OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 24659)
-- Name: appointments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.appointments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.appointments_id_seq OWNER TO postgres;

--
-- TOC entry 4923 (class 0 OID 0)
-- Dependencies: 225
-- Name: appointments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.appointments_id_seq OWNED BY public.appointments.id;


--
-- TOC entry 228 (class 1259 OID 24695)
-- Name: client_medical_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_medical_records (
    id integer NOT NULL,
    client_id integer,
    appointment_id integer,
    employee_id integer,
    record_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    diagnosis text,
    treatment text,
    notes text,
    attachments text
);


ALTER TABLE public.client_medical_records OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 24694)
-- Name: client_medical_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_medical_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.client_medical_records_id_seq OWNER TO postgres;

--
-- TOC entry 4924 (class 0 OID 0)
-- Dependencies: 227
-- Name: client_medical_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_medical_records_id_seq OWNED BY public.client_medical_records.id;


--
-- TOC entry 220 (class 1259 OID 24596)
-- Name: clinics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clinics (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    address character varying(500) NOT NULL,
    phone_number character varying(20),
    email character varying(100),
    is_active boolean DEFAULT true
);


ALTER TABLE public.clinics OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 24595)
-- Name: clinics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clinics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clinics_id_seq OWNER TO postgres;

--
-- TOC entry 4925 (class 0 OID 0)
-- Dependencies: 219
-- Name: clinics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clinics_id_seq OWNED BY public.clinics.id;


--
-- TOC entry 234 (class 1259 OID 24751)
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    clinic_id integer,
    name character varying(255) NOT NULL,
    type character varying(100) NOT NULL,
    serial_number character varying(100),
    model character varying(100),
    purchase_date date,
    status character varying(50) DEFAULT 'ђ Ў®в Ґв'::character varying,
    last_maintenance date,
    next_maintenance date
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 24750)
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_id_seq OWNER TO postgres;

--
-- TOC entry 4926 (class 0 OID 0)
-- Dependencies: 233
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- TOC entry 236 (class 1259 OID 24766)
-- Name: equipment_usage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_usage (
    id integer NOT NULL,
    appointment_id integer,
    equipment_id integer,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    notes text
);


ALTER TABLE public.equipment_usage OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 24765)
-- Name: equipment_usage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_usage_id_seq OWNER TO postgres;

--
-- TOC entry 4927 (class 0 OID 0)
-- Dependencies: 235
-- Name: equipment_usage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_usage_id_seq OWNED BY public.equipment_usage.id;


--
-- TOC entry 230 (class 1259 OID 24720)
-- Name: medications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medications (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    quantity integer DEFAULT 0,
    clinic_id integer DEFAULT 1
);


ALTER TABLE public.medications OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 24719)
-- Name: medications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medications_id_seq OWNER TO postgres;

--
-- TOC entry 4928 (class 0 OID 0)
-- Dependencies: 229
-- Name: medications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medications_id_seq OWNED BY public.medications.id;


--
-- TOC entry 232 (class 1259 OID 24729)
-- Name: prescriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prescriptions (
    id integer NOT NULL,
    medical_record_id integer,
    medication_id integer,
    employee_id integer,
    quantity_prescribed integer NOT NULL
);


ALTER TABLE public.prescriptions OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 24728)
-- Name: prescriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prescriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prescriptions_id_seq OWNER TO postgres;

--
-- TOC entry 4929 (class 0 OID 0)
-- Dependencies: 231
-- Name: prescriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prescriptions_id_seq OWNED BY public.prescriptions.id;


--
-- TOC entry 224 (class 1259 OID 24650)
-- Name: services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.services (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    price numeric(10,2) NOT NULL,
    duration_minutes integer NOT NULL,
    is_active boolean DEFAULT true,
    clinic_id integer DEFAULT 1 NOT NULL
);


ALTER TABLE public.services OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 24649)
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.services_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.services_id_seq OWNER TO postgres;

--
-- TOC entry 4930 (class 0 OID 0)
-- Dependencies: 223
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.services_id_seq OWNED BY public.services.id;


--
-- TOC entry 218 (class 1259 OID 24583)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    first_name character varying(100),
    last_name character varying(100),
    phone_number character varying(20),
    date_of_birth date,
    passport_data text,
    policy_number character varying(50),
    clinic_id integer DEFAULT 1 NOT NULL,
    "position" character varying(100),
    hire_date date,
    description text
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 24582)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4931 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4692 (class 2604 OID 24644)
-- Name: appointment_statuses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointment_statuses ALTER COLUMN id SET DEFAULT nextval('public.appointment_statuses_id_seq'::regclass);


--
-- TOC entry 4696 (class 2604 OID 24663)
-- Name: appointments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments ALTER COLUMN id SET DEFAULT nextval('public.appointments_id_seq'::regclass);


--
-- TOC entry 4699 (class 2604 OID 24698)
-- Name: client_medical_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_medical_records ALTER COLUMN id SET DEFAULT nextval('public.client_medical_records_id_seq'::regclass);


--
-- TOC entry 4690 (class 2604 OID 24599)
-- Name: clinics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clinics ALTER COLUMN id SET DEFAULT nextval('public.clinics_id_seq'::regclass);


--
-- TOC entry 4705 (class 2604 OID 24754)
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- TOC entry 4707 (class 2604 OID 24769)
-- Name: equipment_usage id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_usage ALTER COLUMN id SET DEFAULT nextval('public.equipment_usage_id_seq'::regclass);


--
-- TOC entry 4701 (class 2604 OID 24723)
-- Name: medications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medications ALTER COLUMN id SET DEFAULT nextval('public.medications_id_seq'::regclass);


--
-- TOC entry 4704 (class 2604 OID 24732)
-- Name: prescriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescriptions ALTER COLUMN id SET DEFAULT nextval('public.prescriptions_id_seq'::regclass);


--
-- TOC entry 4693 (class 2604 OID 24653)
-- Name: services id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services ALTER COLUMN id SET DEFAULT nextval('public.services_id_seq'::regclass);


--
-- TOC entry 4686 (class 2604 OID 24586)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4902 (class 0 OID 24641)
-- Dependencies: 222
-- Data for Name: appointment_statuses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.appointment_statuses (id, name, description) FROM stdin;
1	Запланирован	\N
2	Подтвержден	\N
3	Отменен	\N
4	Завершен	\N
\.


--
-- TOC entry 4906 (class 0 OID 24660)
-- Dependencies: 226
-- Data for Name: appointments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.appointments (id, client_id, employee_id, clinic_id, status_id, service_id, appointment_date, appointment_time, duration_minutes, notes, created_at, price) FROM stdin;
3	8	\N	1	1	1	2025-10-27	09:00:00	60	\N	2025-10-28 00:09:21.617453	0.00
4	8	\N	1	1	1	2025-10-29	09:00:00	60	\N	2025-10-28 22:06:59.786584	0.00
5	8	8	1	4	1	2025-10-28	23:00:00	60	\N	2025-10-28 22:08:51.27592	0.00
6	8	8	1	1	1	2025-10-30	23:24:00	60	\N	2025-10-30 23:21:24.522987	0.00
7	8	8	1	1	1	2025-11-06	23:00:00	60	\N	2025-11-06 19:19:38.223968	2500.00
8	8	6	1	1	1	2025-11-13	23:00:00	60	\N	2025-11-13 19:43:27.63003	2500.00
9	8	7	1	1	3	2025-11-13	23:00:00	60	\N	2025-11-13 19:43:37.663213	36400.00
10	8	8	1	1	1	2025-11-13	23:00:00	60	\N	2025-11-13 20:26:30.812952	2500.00
11	14	14	2	4	5	2025-12-02	23:00:00	60	\N	2025-12-02 22:50:27.271248	123.00
\.


--
-- TOC entry 4908 (class 0 OID 24695)
-- Dependencies: 228
-- Data for Name: client_medical_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_medical_records (id, client_id, appointment_id, employee_id, record_date, diagnosis, treatment, notes, attachments) FROM stdin;
1	8	5	8	2025-10-28 22:11:04.847976	аваыаыва	выаываываыва	ываываыа	\N
2	14	11	14	2025-12-02 22:50:36.747588	123	123	123	\N
\.


--
-- TOC entry 4900 (class 0 OID 24596)
-- Dependencies: 220
-- Data for Name: clinics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clinics (id, name, address, phone_number, email, is_active) FROM stdin;
1	Центральная клиника "Зубибиби"	ул. Центральная, 1	+7-123-456-7890	center@zubibibi.ru	t
2	Северная клиника "Зубибиби"	ул. Северная, 2	+7-987-654-3210	north@zubibibi.ru	t
\.


--
-- TOC entry 4914 (class 0 OID 24751)
-- Dependencies: 234
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment (id, clinic_id, name, type, serial_number, model, purchase_date, status, last_maintenance, next_maintenance) FROM stdin;
\.


--
-- TOC entry 4916 (class 0 OID 24766)
-- Dependencies: 236
-- Data for Name: equipment_usage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_usage (id, appointment_id, equipment_id, start_time, end_time, notes) FROM stdin;
\.


--
-- TOC entry 4910 (class 0 OID 24720)
-- Dependencies: 230
-- Data for Name: medications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medications (id, name, description, quantity, clinic_id) FROM stdin;
\.


--
-- TOC entry 4912 (class 0 OID 24729)
-- Dependencies: 232
-- Data for Name: prescriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prescriptions (id, medical_record_id, medication_id, employee_id, quantity_prescribed) FROM stdin;
\.


--
-- TOC entry 4904 (class 0 OID 24650)
-- Dependencies: 224
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.services (id, name, description, price, duration_minutes, is_active, clinic_id) FROM stdin;
1	Консультация стоматолога	Комплексный осмотр и диагностика состояния здоровья, составление индивидуального плана лечения	2500.00	60	t	1
3	Брекеты	Установка Брекетов	36400.00	45	t	1
5	123	123	123.00	3	t	2
\.


--
-- TOC entry 4898 (class 0 OID 24583)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, role, is_active, created_at, first_name, last_name, phone_number, date_of_birth, passport_data, policy_number, clinic_id, "position", hire_date, description) FROM stdin;
1	YaKakal	kakal@mail.ru	$2b$12$oAjDmbqy3yelyx9xCkTwB.cHf6NfbY8br92krUa9boPizGkq0DOLC	client	t	2025-10-23 21:29:10.131024	Тимофей	Шавшуков	+8 800 55 35 35	\N	\N	\N	1	\N	\N	\N
2	dr_ivanov	ivanov@clinic.ru	hash1	doctor	t	2025-10-25 13:14:29.485655	Иван	Иванов	+7 (912) 345-67-89	\N	\N	\N	1	Стоматолог-терапевт	2015-06-15	Специалист по лечению кариеса и заболеваний дёсен
3	dr_petrova	petrova@clinic.ru	hash2	doctor	t	2025-10-25 13:14:29.485655	Мария	Петрова	+7 (912) 345-67-90	\N	\N	\N	1	Стоматолог-ортодонт	2018-03-22	Эксперт по исправлению прикуса и установке брекетов
4	dr_sidorov	sidorov@clinic.ru	hash3	doctor	t	2025-10-25 13:14:29.485655	Алексей	Сидоров	+7 (912) 345-67-91	\N	\N	\N	1	Хирург-стоматолог	2012-11-10	Проводит сложные хирургические операции
5	dr_kuznetsova	kuznetsova@clinic.ru	hash4	doctor	t	2025-10-25 13:14:29.485655	Елена	Кузнецова	+7 (912) 345-67-92	\N	\N	\N	1	Детский стоматолог	2019-09-05	Специализируется на лечении зубов у детей
6	dr_vorobev	vorobev@clinic.ru	hash5	doctor	t	2025-10-25 13:14:29.485655	Дмитрий	Воробьёв	+7 (912) 345-67-93	\N	\N	\N	1	Стоматолог-ортопед	2016-07-18	Занимается протезированием и восстановлением зубов
7	dr_romanova	romanova@clinic.ru	hash6	doctor	t	2025-10-25 13:14:29.485655	Ольга	Романова	+7 (912) 345-67-94	\N	\N	\N	1	Пародонтолог	2014-12-03	Специалист по лечению заболеваний дёсен
8	123	123@mail.ru	$2b$12$A6ibLJPAVe48rxOj94jrYe8Cm6fPCdyxK6qI6NmGq8PLgXCHrR8V6	doctor	t	2025-10-25 14:05:19.09635	Тимофей	\N	\N	\N	\N	\N	1	\N	\N	\N
9	1234	1234@123	$2b$12$fb8xHHhVVS0Qn62YRzQOnueY8ie0rrkS9GjOVVSxB96WsTMDM41Dy	client	t	2025-12-02 22:02:45.458599	\N	\N	\N	\N	\N	\N	1	\N	\N	\N
12	12345	12345@mail.ru	$2b$12$tM/sk2TsH9/hw2Y4cGZw0Ol8iP627.k3CSTQ0cMovzDAO/J.YuHrm	client	t	2025-12-02 22:35:48.585766	\N	\N	\N	\N	\N	\N	1	\N	\N	\N
13	123456	123456@mail.ru	$2b$12$xAOwsZ.4yPhDVh4/TI8W8.C5tK2V.XAdMZJghTjul/GKc2HM4B5m.	client	t	2025-12-02 22:38:30.900936	\N	\N	\N	\N	\N	\N	1	\N	\N	\N
14	1	1@mail.ru	$2b$12$jdyLgrYA1JNh96rh/L1ebeilQ/pvNREFjTKAmrwe.ECM9zjsRfJxy	doctor	t	2025-12-02 22:40:37.252604	Тима	Шиш	123123123	\N	\N	\N	2	Пародонтолог	\N	\N
\.


--
-- TOC entry 4932 (class 0 OID 0)
-- Dependencies: 221
-- Name: appointment_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.appointment_statuses_id_seq', 1, false);


--
-- TOC entry 4933 (class 0 OID 0)
-- Dependencies: 225
-- Name: appointments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.appointments_id_seq', 11, true);


--
-- TOC entry 4934 (class 0 OID 0)
-- Dependencies: 227
-- Name: client_medical_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_medical_records_id_seq', 2, true);


--
-- TOC entry 4935 (class 0 OID 0)
-- Dependencies: 219
-- Name: clinics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clinics_id_seq', 1, false);


--
-- TOC entry 4936 (class 0 OID 0)
-- Dependencies: 233
-- Name: equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_id_seq', 1, false);


--
-- TOC entry 4937 (class 0 OID 0)
-- Dependencies: 235
-- Name: equipment_usage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_usage_id_seq', 1, false);


--
-- TOC entry 4938 (class 0 OID 0)
-- Dependencies: 229
-- Name: medications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medications_id_seq', 2, true);


--
-- TOC entry 4939 (class 0 OID 0)
-- Dependencies: 231
-- Name: prescriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prescriptions_id_seq', 1, false);


--
-- TOC entry 4940 (class 0 OID 0)
-- Dependencies: 223
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.services_id_seq', 5, true);


--
-- TOC entry 4941 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 14, true);


--
-- TOC entry 4719 (class 2606 OID 24648)
-- Name: appointment_statuses appointment_statuses_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointment_statuses
    ADD CONSTRAINT appointment_statuses_name_key UNIQUE (name);


--
-- TOC entry 4721 (class 2606 OID 24646)
-- Name: appointment_statuses appointment_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointment_statuses
    ADD CONSTRAINT appointment_statuses_pkey PRIMARY KEY (id);


--
-- TOC entry 4725 (class 2606 OID 24668)
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- TOC entry 4727 (class 2606 OID 24703)
-- Name: client_medical_records client_medical_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_medical_records
    ADD CONSTRAINT client_medical_records_pkey PRIMARY KEY (id);


--
-- TOC entry 4717 (class 2606 OID 24604)
-- Name: clinics clinics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clinics
    ADD CONSTRAINT clinics_pkey PRIMARY KEY (id);


--
-- TOC entry 4733 (class 2606 OID 24759)
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- TOC entry 4735 (class 2606 OID 24773)
-- Name: equipment_usage equipment_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_usage
    ADD CONSTRAINT equipment_usage_pkey PRIMARY KEY (id);


--
-- TOC entry 4729 (class 2606 OID 24727)
-- Name: medications medications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medications
    ADD CONSTRAINT medications_pkey PRIMARY KEY (id);


--
-- TOC entry 4731 (class 2606 OID 24734)
-- Name: prescriptions prescriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 4723 (class 2606 OID 24658)
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- TOC entry 4711 (class 2606 OID 24594)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4713 (class 2606 OID 24590)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4715 (class 2606 OID 24592)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4708 (class 1259 OID 24794)
-- Name: idx_users_clinic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_clinic_id ON public.users USING btree (clinic_id);


--
-- TOC entry 4709 (class 1259 OID 24793)
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_role ON public.users USING btree (role);


--
-- TOC entry 4738 (class 2606 OID 24795)
-- Name: appointments appointments_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4739 (class 2606 OID 24853)
-- Name: appointments appointments_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- TOC entry 4740 (class 2606 OID 24800)
-- Name: appointments appointments_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.users(id);


--
-- TOC entry 4741 (class 2606 OID 24689)
-- Name: appointments appointments_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- TOC entry 4742 (class 2606 OID 24684)
-- Name: appointments appointments_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.appointment_statuses(id);


--
-- TOC entry 4743 (class 2606 OID 24709)
-- Name: client_medical_records client_medical_records_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_medical_records
    ADD CONSTRAINT client_medical_records_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointments(id);


--
-- TOC entry 4744 (class 2606 OID 24805)
-- Name: client_medical_records client_medical_records_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_medical_records
    ADD CONSTRAINT client_medical_records_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4745 (class 2606 OID 24810)
-- Name: client_medical_records client_medical_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_medical_records
    ADD CONSTRAINT client_medical_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.users(id);


--
-- TOC entry 4749 (class 2606 OID 24760)
-- Name: equipment equipment_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id) ON DELETE CASCADE;


--
-- TOC entry 4750 (class 2606 OID 24774)
-- Name: equipment_usage equipment_usage_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_usage
    ADD CONSTRAINT equipment_usage_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointments(id) ON DELETE CASCADE;


--
-- TOC entry 4751 (class 2606 OID 24779)
-- Name: equipment_usage equipment_usage_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_usage
    ADD CONSTRAINT equipment_usage_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- TOC entry 4746 (class 2606 OID 24815)
-- Name: prescriptions prescriptions_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.users(id);


--
-- TOC entry 4747 (class 2606 OID 24735)
-- Name: prescriptions prescriptions_medical_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_medical_record_id_fkey FOREIGN KEY (medical_record_id) REFERENCES public.client_medical_records(id) ON DELETE CASCADE;


--
-- TOC entry 4748 (class 2606 OID 24740)
-- Name: prescriptions prescriptions_medication_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_medication_id_fkey FOREIGN KEY (medication_id) REFERENCES public.medications(id);


--
-- TOC entry 4737 (class 2606 OID 24858)
-- Name: services services_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- TOC entry 4736 (class 2606 OID 24863)
-- Name: users users_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


-- Completed on 2025-12-02 22:59:51

--
-- PostgreSQL database dump complete
--

\unrestrict LUCVenvlXW37VAYH0qSccbqoXHFcdxtPZ7uzOmTMyo780HX5UofA8xs2V8rreeC

