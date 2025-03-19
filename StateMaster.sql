
Create Table TmpStateMaster(
    StateId int,
    StateName varchar(100),
    NationalityID int,
    LocalName varchar(100),
    Active char,
    LastModifiedDate TIMESTAMPTZ,
    LastModifiedBy int,
    MachineAddress varchar(100)
);

INSERT into TmpStateMaster (StateID, StateName, NationalityID, LocalName, Active, LastModifiedDate, LastModifiedBy, MachineAddress) VALUES
 (1, N'Andeman & nicobar', 80, N'Andeman & nicobar', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(2, N'Andhra pradesh', 80, N'Andhra pradesh', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(3, N'Arunachal pradesh', 80, N'Arunachal pradesh', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(4, N'Assam', 80, N'Assam', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(5, N'Bihar', 80, N'Bihar', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(6, N'Chandigarh', 80, N'Chandigarh', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(7, N'Daman & diu', 80, N'Daman & diu', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(8, N'Delhi', 80, N'Delhi', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(9, N'Dadra & nagar haveli', 80, N'Dadra & nagar haveli', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(10, N'Goa', 80, N'Goa', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(11, N'Gujarat', 80, N'Gujarat', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(12, N'Himachal pradesh', 80, N'Himachal pradesh', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(13, N'Haryana', 80, N'Haryana', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(14, N'Jammu & kashmir', 80, N'Jammu & kashmir', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(15, N'Kerala', 80, N'Kerala', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(16, N'Karnataka', 80, N'Karnataka', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(17, N'Lakshadweep', 80, N'Lakshadweep', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(18, N'Meghalaya', 80, N'Meghalaya', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(19, N'Maharashtra', 80, N'Maharashtra', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(20, N'Manipur', 80, N'Manipur', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(21, N'Madhya pradesh', 80, N'Madhya pradesh', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(22, N'Mizoram', 80, N'Mizoram', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(23, N'Nagaland', 80, N'Nagaland', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(24, N'Orissa', 80, N'Orissa', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(25, N'Punjab', 80, N'Punjab', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(26, N'Pondicherry', 80, N'Pondicherry', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(27, N'Rajasthan', 80, N'Rajasthan', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(28, N'Sikkim', 80, N'Sikkim', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(29, N'Tamilnadu', 80, N'Tamilnadu', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(30, N'Tripura', 80, N'Tripura', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(31, N'Uttar pradesh', 80, N'Uttar pradesh', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(32, N'West bengal', 80, N'West bengal', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(33, N'Chhattisgarh', 80, N'Chhattisgarh', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(34, N'Jharkhand', 80, N'Jharkhand', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(35, N'Uttranchal', 80, N'Uttranchal', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(40, N'Out of Country', 80, N'Out of Country', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(41, N'Internet', 80, N'Internet', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad'),
(2017000001, N'Telangana', 80, N'Telangana', N'Y', CAST(N'2022-07-14T10:02:57.520' AS TIMESTAMPTZ), 0, N'InitalLoad');

insert into mdm_statemaster 
select stateId,stateName,active,lastmodifieddate from TmpStateMaster

