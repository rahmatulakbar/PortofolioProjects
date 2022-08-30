select*
from PortofolioProject..kematian
select*
from PortofolioProject..vaksinasi

--total kasus, total kematian, dan persentase kematian setiap negara perhari
select location,date,population,total_cases,total_deaths,(total_deaths/total_cases)*100 PersenKematian
from PortofolioProject..kematian
where continent is not null
order by location,date

-- kasus total setiap negara
select location,population,max(cast(total_cases as int)) jumlah_kasus,max(cast(total_deaths as int)) jumlah_kematian,max(total_deaths/total_cases)*100 TotalPersenKematian
from PortofolioProject..kematian
where continent is not null
group by location,population
order by location

--urutan negara dengan jumlah kematian terbanyak
select location,population,max(cast(total_deaths as int)) total_kematian
from PortofolioProject..kematian
where continent is not null
group by location,population
order by total_kematian desc
 
 --join tabel
 select k.location,k.total_cases,v.total_vaccinations
 from PortofolioProject..kematian k
 join PortofolioProject..vaksinasi v
	on k.location = v.location
	and k.date = v.date
order by k.location

--persentase vaksinasi setiap negara perhari
select k.location,k.population,k.total_cases, v.total_vaccinations,(v.total_vaccinations/k.total_cases)*100 persen_vaksin
 from PortofolioProject..kematian k
 join PortofolioProject..vaksinasi v
	on k.location = v.location
	and k.date = v.date
order by k.location

--total vaksinasi setiap negara
select k.location,k.population,max(cast(k.total_cases as int)) total_kasus, max(cast(v.total_vaccinations as int)) total_vaksin,(max(cast(v.total_vaccinations as int))/max(k.total_cases))*100 persen_total_vaksin
 from PortofolioProject..kematian k
 join PortofolioProject..vaksinasi v
	on k.location = v.location
	and k.date = v.date
where k.continent is not null
group by k.location,k.population
order by k.location

--vaksin perhari dan total 
select k.location,k.population,convert(int,v.new_vaccinations) vaksin_baru,
sum(convert(int,v.new_vaccinations))over(partition by k.location order by k.location,k.date) total
 from PortofolioProject..kematian k
 join PortofolioProject..vaksinasi v
	on k.location = v.location
	and k.date = v.date
where k.continent is not null
order by k.location

--persentase total vaksinasi (temp tabel)

drop table if exists #persentasevaksin
create table #persentasevaksin
(location nvarchar(255),
population numeric,
vaksin_baru numeric,
total numeric)

insert into #persentasevaksin
select k.location,k.population,convert(int,v.new_vaccinations) vaksin_baru,
sum(convert(int,v.new_vaccinations))over(partition by k.location order by k.location,k.date) total
 from PortofolioProject..kematian k
 join PortofolioProject..vaksinasi v
	on k.location = v.location
	and k.date = v.date
where k.continent is not null
order by k.location

select*, (total/population)*100
from #persentasevaksin

