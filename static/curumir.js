let currentCountry = 'ru';
let currentDate = '2020-02-05';
let currentArea = '1317';
let tags = {};

function listContent(keyword='python')
{
    if (keyword == '') { keyword = 'None'}
    fetch('/list/'+keyword)
    .then(resp => resp.json())
    .then(data => {
        const nbList = document.getElementById('notebooks-list');
        while (nbList.firstChild) { nbList.removeChild(nbList.firstChild); }
        for (let element of data)
        {
            let notebookElem = document.createElement('span');
            // console.log(element)
            notebookElem.innerHTML = `${element['name']}</br><span style="color: var(--highL)">${element['area']['name']}</span>`;
            notebookElem.className = 'nb-li';
            notebookElem.addEventListener('click', () => { showCard(element); })

            let skillsEl = document.createElement('ul');
            // skillsEl.className = 'nb-li';
            for (let skill of element['key_skills'])
            {
                let notebookEl = document.createElement('li');
                notebookEl.innerText = skill['name'];
                notebookEl.className = 'nb-li';
                skillsEl.appendChild(notebookEl);
            }
            nbList.appendChild(notebookElem);
            nbList.appendChild(skillsEl);

            if (data.indexOf(element) != data.length-1) { nbList.appendChild(document.createElement('hr')); }
            
        }
        document.getElementById('notebook-controls').innerHTML = `<span>${data.length} вакансий</span>`;

    });
}

function showCard(card)
{
    const cont = document.getElementById('modal');
    createCard(card).then(el => { cont.appendChild(el); });
    cont.parentNode.classList.toggle('off');
}

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

function setCurrentDate(date)
{
    currentDate = date;
    if (document.querySelector('span.date-option.active')) { document.querySelector('span.date-option.active').classList.remove('active') }
    document.querySelector('#date-'+date).classList.add('active');
}

function getAreaClusters(country=null, area=null, date=null)
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
                let skill_tags = Object.keys(tags).includes(skill) ? ` cursor: pointer;" onclick="showSkillTags('${skill}', this)"` : '"'
                clusterData.innerHTML += data[3].includes(skill) ? 
                `<span id="skill-${skill}" class="skill center" style="${skill_tags} >${skill}</span>, ` : 
                `<span id="skill-${skill}" class="skill" style="${skill_tags} >${skill}</span>, `;
            }
            clusterData.innerHTML = clusterData.innerHTML.replace(/,\s*$/gm, ''); // регулярка, чтобы убрать лишнюю запятую в конце
            container.appendChild(clusterData);
        }
        // cInfo.innerHTML = `Вакансий: ${data[0]}. Порог: ${data[1]}. Навыков: ${skills_counter}. Кластеров: ${data[3].length}. Силуэт: ${data[4].toFixed(6)}`;
        cInfo.innerHTML = `Вакансий: ${data[0]}. Порог: ${data[1]}. Навыков: ${skills_counter}. Кластеров: ${data[3].length}.`;
        // Жесткий хак, чтобы нащелкать скриншотов для статьи, НЕ ИСПОЛЬЗОВАТЬ БОЛЬШЕ НИКАК
        // cInfo.style.fontSize = '22px';
        // cInfo.innerHTML = `Region: Sverdlovsk Oblast
        // <div style="font-size: 0.8em;">Vacancies: ${data[0]}. Threshold: ${data[1]}. Skills: ${skills_counter}. Clusters: ${data[3].length}. Silhouette: ${data[4].toFixed(6)}</div>`;
    });
}

async function createCard(card)
{
    let cardElement = document.createElement('div');
    // cardElement.id = card['id'];
    cardElement.className = 'card';

    let cardTitle = document.createElement('h3');
    cardTitle.innerText = card['name'];

    let ar = document.createElement('p');
    ar.innerHTML = card['area']['name'];
    ar.style.color = 'var(--highL)';

    let descr = document.createElement('p');
    descr.innerHTML = card['description'];

    let closeBtn = document.createElement('button');
    closeBtn.innerText = 'Закрыть';
    closeBtn.className = 'nb-btn';
    closeBtn.addEventListener('click', closeCardView);

    cardElement.appendChild(cardTitle);
    cardElement.appendChild(ar);
    cardElement.appendChild(descr);
    cardElement.appendChild(closeBtn);
    
    return cardElement;
}

function closeCardView()
{
    const modal = document.getElementById('modal');
    modal.removeChild(modal.firstChild);
    modal.parentNode.classList.toggle('off');
}

/* 
    Тут обрабатываем рекомендации схожих скиллов для пользователя
    Есть дублирующий код, но пока рефакторинг не в приоритете
*/


/** Отрендрить элементы для настройки рекомендаций по стране */
function contextSetup(country='ru')
{
    fetch(`/country?c=${country}`)
    .then(resp => resp.json())
    .then(data => {
        const areasContainer = document.querySelector('#areas-list');
        areasContainer.innerHTML = '<div class="content-meta">Регион</div>';
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
        datesContainer.innerHTML = '<div class="content-meta">Период</div>';
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
    const country = document.querySelector('#country-list').querySelector('select').value;
    const area = document.querySelector('#areas-list').querySelector('select').value;
    const date = document.querySelector('#dates-list').querySelector('select').value;
    const skills = document.querySelector('#finder-skills').value;
    console.log(country, area, date, skills);
    fetch(`/context?skills=${skills}&date=${date}&area=${area}&country=${country}`)
    .then(resp => resp.json())
    .then(data => {
        console.log(data)
        const container = document.querySelector('#area-clusters');
        container.innerHTML = '';
        let cInfo = document.createElement('div');
        container.appendChild(cInfo);
        // перевести все скиллы в нижний регистр
        let lowerSkills = skills.split(',').map(function (val) { return val.toLowerCase(); })
        for (let cluster of data[2])
        {
            let clusterData = document.createElement('div');
            clusterData.className = 'cluster';
            clusterData.innerHTML = `<strong>Набор ${data[2].indexOf(cluster)+1} (навыков: ${cluster.length})</strong>: `;
            for (let skill of cluster)
            {
                let skill_tags = Object.keys(tags).includes(skill) ? ` cursor: pointer;" onclick="showSkillTags('${skill}', this)"` : '"'
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

document.addEventListener('click', function(evt) {
    const controls = document.querySelector('#skill-tags');
    if (controls)
    {
        if (!controls.contains(evt.target) && !controls.parentNode.contains(evt.target)) controls.remove();
    }
});
