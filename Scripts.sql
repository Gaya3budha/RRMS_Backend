-- scripts to insert into roles table
insert into mdm_role values(1,'Admin','Y',current_date,current_date),
(2,'User','Y',current_date,current_date),
(3,'ContentManager','Y',current_date,current_date);

insert into public.mdm_department values(1,'Forest Cell','Y',current_date);
insert into public.mdm_department values(2,'Cyber Crime and Narcotics','Y',current_date);
insert into public.mdm_department values(3,'Economic Offenses','Y',current_date);
insert into public.mdm_department values(4,'CID','Y',current_date);

-- scripts to insert into Division master table
insert into mdm_divisionmaster values(1,'CID','Y',current_date),
(2,'Cyber Crime and Narcotics','Y',current_date),
 (3,'Economic Offences','Y',current_date),
(4,'Forest Cell.CID','Y',current_date),
(5,'Administration','Y',current_date),
(6,'Narcotics & Organized Crime Division','Y',current_date),
(7,'Cyber Crime Division','Y',current_date),
(8,'Deposit Fraud Investigation Division','Y',current_date),
(9,'Special Enquiry Division','Y',current_date),
(10,'Criminal Intelligence Unit','Y',current_date),
(11,'Financial Intelligence Unit','Y',current_date),
(12,'Homicide and Burglary','Y',current_date),
(13,'Anti-Human Traffic Unit','Y',current_date),
(14,' Cyber Training and Research Unit','Y',current_date),
(15,'Deposit Fraud Investigation Division Under DIGP Economic Officences','Y',current_date);




insert into mdm_designationmaster values(1,'Director General of Police','Y',current_date),
(2,'Addl. Director General of Police','Y',current_date),
 (3,'Deputy Inspector General of Police','Y',current_date),
(4,'Superintendent of Police','Y',current_date);


-- generalLokup Script
insert into public.mdm_generallookup values(1,'Investigation',1,'Y',CURRENT_DATE,1);
insert into public.mdm_generallookup values(2,'Enquiry',1,'Y',CURRENT_DATE,2);
insert into public.mdm_generallookup values(3,'Case Files',2,'Y',CURRENT_DATE,1);
insert into public.mdm_generallookup values(4,'Correspondence',2,'Y',CURRENT_DATE,2);
insert into public.mdm_generallookup values(5,'Public',7,'Y',CURRENT_DATE,1);
insert into public.mdm_generallookup values(6,'Confidential',7,'Y',CURRENT_DATE,2);
insert into public.mdm_generallookup values(20,'Image',5,'Y',CURRENT_DATE,1);
insert into public.mdm_generallookup values(21,'Document',5,'Y',CURRENT_DATE,2);
insert into public.mdm_generallookup values(22,'Audio',5,'Y',CURRENT_DATE,3);
insert into public.mdm_generallookup values(23,'Video',5,'Y',CURRENT_DATE,4);

insert into public.mdm_generallookup("lookupName","CategoryId",active,"lastmodifiedDate") 
select "fileTypeName",3,'Y',current_date from public.mdm_filetype

insert into public.mdm_generallookup("lookupName","CategoryId",active,"lastmodifiedDate") 
select "statusName",6,'Y',current_date from public.mdm_casestatus


insert into public.mdm_division values(1,'Traffic & Transport Division','Y',current_date,1);
insert into public.mdm_division values(2,'Cyber Crime Division(CCD)','Y',current_date,2);
insert into public.mdm_division values(3,'Narcotics and Organized Crime Division','Y',current_date,2);
insert into public.mdm_division values(4,'Cyber Training & Research Center','Y',current_date,2);
insert into public.mdm_division values(5,'Special Enquiry Division(SED)','Y',current_date,4);
insert into public.mdm_division values(6,'Administration','Y',current_date,4);
insert into public.mdm_division values(7,'Criminial Intelligence Unit(CIU)','Y',current_date,4);
insert into public.mdm_division values(8,'Homicide & Burglary Division','Y',current_date,4);
insert into public.mdm_division values(9,'Deposits Fraud Investigation Division','Y',current_date,3);
insert into public.mdm_division values(10,'Economic Offenses Division','Y',current_date,3);
insert into public.mdm_division values(11,'Financial Intelligence Unit','Y',current_date,3);
insert into public.mdm_division values(12,'Anti Human Trafficking Unit','Y',current_date,3);

