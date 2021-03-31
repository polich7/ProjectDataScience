let currentCountry = 'ru';
let currentDate = '2020-02-05';
let currentArea = '1317';


function getCountryData(country='ru')
{
    fetch(`/country?c=${country}`)
    .then(resp => resp.json())
    .then(data => {
        const areasContainer = document.querySelector('#areas-list');
        areasContainer.innerHTML = '<div class="content-meta">Регион</div>';
        const areaSelector = document.createElement('select');
        areasContainer.appendChild(areaSelector);
        areaSelector.onchange = () => {
            currentArea = areaSelector.value;
            getAreaClusters();
        }
        for (let code of Object.keys(data[0]))
        {
            let areaItem = document.createElement('option');
            areaItem.innerHTML = data[0][code];
            areaItem.id = 'area-'+code;
            areaItem.value = code;
            areaSelector.appendChild(areaItem);
        }
        const datesContainer = document.querySelector('#dates-list');
        datesContainer.innerHTML = '';
        for (let date of data[1])
        {
            let dateItem = document.createElement('span');
            dateItem.className = 'date-option';
            dateItem.innerHTML = new Date(date).toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' });
            dateItem.id = `date-${date}`;
            dateItem.onclick = () => { setCurrentDate(date); getAreaClusters(); }
            datesContainer.appendChild(dateItem);
        }
        currentCountry = country;
        let defaultArea = country == 'ru' ? Object.keys(data[0])[26] : Object.keys(data[0])[2]
        setCurrentDate(data[1][data[1].length-1]);
        currentArea = defaultArea;
        areaSelector.value = defaultArea;
        getAreaClusters();
    });
}

function setCurrentDate(date) // по умолчанию выставлять последний существующий период
{
    currentDate = date;
    if (document.querySelector('span.date-option.active')) { document.querySelector('span.date-option.active').classList.remove('active') }
    document.querySelector('#date-'+date).classList.add('active');
}

function getAreaClusters(country=null, area=null, date=null) // отображаем кластеры в регионе
{
    let c = country ? country : currentCountry;
    let a = area ? area : currentArea;
    let d = date ? date : currentDate;
    fetch(`/clusters?date=${d}&area=${a}&country=${c}`)
    .then(resp => resp.json())
    .then(data => {
        const container = document.querySelector('#area-clusters');
        container.innerHTML = '';
        let cInfo = document.createElement('div');
        container.appendChild(cInfo);
        let skills_counter = 0;
        for (let cluster of data[2])
        {
            let clusterData = document.createElement('div');
            clusterData.className = 'cluster';
            // clusterData.innerHTML = `<strong>Cluster ${data[2].indexOf(cluster)+1} (skills: ${cluster.length})</strong>: `;
            clusterData.innerHTML = `<strong>Кластер ${data[2].indexOf(cluster)+1} (навыков: ${cluster.length})</strong>: `;
            skills_counter += cluster.length;
            for (let skill of cluster)
            {
                let skill_tags =  '"'
                clusterData.innerHTML += data[3].includes(skill) ?
                `<span id="skill-${skill}" class="skill center" style="${skill_tags} >${skill}</span>, ` : 
                `<span id="skill-${skill}" class="skill" style="${skill_tags} >${skill}</span>, `;
            }
            clusterData.innerHTML = clusterData.innerHTML.replace(/,\s*$/gm, ''); // регулярка, чтобы убрать лишнюю запятую в конце
            container.appendChild(clusterData);
        }
        cInfo.innerHTML = `Вакансий: ${data[0]}. Порог: ${data[1]}. Навыков: ${skills_counter}. Кластеров: ${data[3].length}.`;
    });
}

/* 
    Тут обрабатываем рекомендации схожих скиллов для пользователя
    Есть дублирующий код, но пока рефакторинг не в приоритете
*/


/** Отрендрить элементы для настройки рекомендаций по стране */
function contextSetup(country='ru') // подгружаем список регионов и месяцев в соответсвии с настройками
{
    fetch(`/country?c=${country}`)
    .then(resp => resp.json())
    .then(data => {
        const areasContainer = document.querySelector('#areas-list');
        areasContainer.innerHTML = '<div class="content-meta">Регион</div>'; //тут подгружаются регионы
        const areaSelector = document.createElement('select');
        areasContainer.appendChild(areaSelector);
        for (let code of Object.keys(data[0]))
        {
            let areaItem = document.createElement('option');
            areaItem.innerHTML = data[0][code];
            areaItem.id = `area-${code}`;
            areaItem.value = code;
            areaSelector.appendChild(areaItem);
        }

        const datesContainer = document.querySelector('#dates-list');
        datesContainer.innerHTML = '<div class="content-meta">Период</div>'; // тут грузятся периоды
        const dateSelector = document.createElement('select');
        datesContainer.appendChild(dateSelector);
        for (let date of data[1])
        {
            let dateItem = document.createElement('option');
            dateItem.innerHTML = new Date(date).toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' });
            dateItem.id = `date-${date}`;
            dateItem.value = date;
            dateSelector.appendChild(dateItem);
        }

        setCurrentDate(data[1][data[1].length-1]);
        areaSelector.value = country == 'ru' ? Object.keys(data[0])[26] : Object.keys(data[0])[2];
        dateSelector.value = currentDate;
    });
}

/** Запросить контекст для введенных навыков в рамках выбранных страны, региона и времени*/
function getContext()
{
    const country = document.querySelector('#country-list').querySelector('select').value; // собираем параметры ииз форм ввода
    const area = document.querySelector('#areas-list').querySelector('select').value;
    const date = document.querySelector('#dates-list').querySelector('select').value;
    const skills = document.querySelector('#finder-skills').value;
    console.log(country, area, date, skills);
    fetch(`/context?skills=${skills}&date=${date}&area=${area}&country=${country}`) // пересылаем на сревер get -запрос с параметрами ->получаем ответ
    .then(resp => resp.json()) // байты декодирууем в json
    .then(data => { // data -получили данные в формате json
        console.log(data)
        const container = document.querySelector('#area-clusters');
        container.innerHTML = '';
        let cInfo = document.createElement('div');
        container.appendChild(cInfo);
        // перевести все скиллы в нижний регистр
        let lowerSkills = skills.split(',').map(function (val) { return val.toLowerCase(); })
        for (let cluster of data[2]) // тут в кластеры и подсветка
        {
            let clusterData = document.createElement('div');
            clusterData.className = 'cluster';
            clusterData.innerHTML = `<strong>Набор ${data[2].indexOf(cluster)+1} (навыков: ${cluster.length})</strong>: `;
            for (let skill of cluster)
            {
                let skill_tags =  '"'
                clusterData.innerHTML += lowerSkills.includes(skill.toLowerCase()) ?
                `<span id="skill-${skill}" class="skill context" style="${skill_tags} >${skill}</span>, ` : data[3].includes(skill) ? 
                `<span id="skill-${skill}" class="skill center" style="${skill_tags} >${skill}</span>, ` : 
                `<span id="skill-${skill}" class="skill" style="${skill_tags} >${skill}</span>, `;
            }
            clusterData.innerHTML = clusterData.innerHTML.replace(/,\s*$/gm, '');
            container.appendChild(clusterData);
        }
    });
}

