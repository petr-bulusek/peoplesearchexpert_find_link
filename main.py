from typing import Optional
import logging
import requests

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

STATES_ABBR_DICT = {'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ',
                    'arkansas': 'AR', 'california': 'CA',
                    'colorado': 'CO', 'connecticut': 'CT',
                    'washington dc': 'DC', 'delaware': 'DE',
                    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
                    'idaho': 'ID', 'illinois': 'IL',
                    'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
                    'kentucky': 'KY', 'louisiana': 'LA',
                    'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA',
                    'michigan': 'MI', 'minnesota': 'MN',
                    'mississippi': 'MS', 'missouri': 'MO', 'montana': 'MT',
                    'nebraska': 'NE', 'nevada': 'NV',
                    'new hampshire': 'NH', 'new jersey': 'NJ',
                    'new mexico': 'NM', 'new york': 'NY',
                    'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH',
                    'oklahoma': 'OK', 'oregon': 'OR',
                    'pennsylvania': 'PA', 'rhode island': 'RI',
                    'south carolina': 'SC', 'south dakota': 'SD',
                    'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
                    'vermont': 'VT', 'virginia': 'VA',
                    'washington': 'WA', 'west virginia': 'WV',
                    'wisconsin': 'WI', 'wyoming': 'WY'}


def get_state_abbr(state_name: str) -> Optional[str]:
    """
    Returns abbreviation of USA state name or none if not found.
    :param state_name: state name e.g. 'Texas'
    :return: state abbreviation e.g. 'TX'
    """
    state_abbr = STATES_ABBR_DICT.get(state_name.lower())
    return state_abbr


def check_input_valid(ppi_data: dict) -> bool:
    """
    Function checks if dict ppi_data contains necessary keys: 'First Name', 'Last Name', 'State', 'City'
    and values for them are not empty.
    :param ppi_data: dictionary containing user data
    :return: True if valid, False if not
    """
    valid = True
    for key in ['First Name', 'Last Name', 'State', 'City']:
        if key not in ppi_data:
            logger.error(f'missing input key {key}')
            valid = False
        elif not len(ppi_data[key]) > 0:
            logger.error(f'missing data for key {key}')
            valid = False
    return valid


def get_link_to_details(ppi_data: dict) -> Optional[str]:
    """
    Checks the page peoplesearchexpert.com if it contains link to user data.
    If yes, returns the link with details, else None.
    :param ppi_data: dictionary containing user data
    necessary keys: 'First Name', 'Last Name', 'State', 'City'
    :return: link with details or None
    """
    logger.debug(f'Searching {ppi_data}')
    if not check_input_valid(ppi_data):
        return None

    state = ppi_data['State']
    state_abbr = get_state_abbr(state_name=state)
    if state_abbr is None:
        logger.debug(f'Unsupported state name {state}')
        return None

    first_name = ppi_data['First Name']
    last_name = ppi_data['Last Name']
    city = ppi_data['City']

    full_name = first_name + ' ' + last_name
    query_url = f'https://www.peoplesearchexpert.com/search?q[full_name]={full_name}&q[location]={city},+{state_abbr}'
    response = requests.get(query_url)
    if response.status_code != requests.codes.ok:
        logger.error('Server response error')
        return None

    name_for_link = full_name.lower().replace(' ', '-')
    results_link = f'https://www.peoplesearchexpert.com/people/{name_for_link}'
    response_html = response.text

    if response_html.count(results_link) > 0:  # contains user info
        state_for_link = state.replace(' ', '+')
        city_for_link = city.lower().replace(' ', '-')
        details_link = results_link + f'?state={state_for_link}#{city_for_link}'
        logger.debug('Result found')
        return details_link
    logger.debug('No result found')
    return None


if __name__ == '__main__':
    set1 = {
        'First Name': 'Bob',
        'Last Name': 'Smith',
        'Middle Initial': '',
        'State': 'Texas',
        'City': 'Houston'
    }
    set2 = {
        'First Name': 'Rob',
        'Last Name': 'Corbova',
        'Middle Initial': 'L',
        'State': 'Columbus',
        'City': 'Ohio'
    }
    set3 = {
        'First Name': 'Shaun',
        'Last Name': 'White',
        'Middle Initial': '',
        'State': 'New York',
        'City': 'New York'
    }
    set_missing_input1 = {
        'First Name': '',
        'Last Name': 'Corbova',
        'Middle Initial': 'L',
        'State': 'Columbus',
        'City': 'Ohio'
    }
    set_missing_input2 = {
        'First Name': 'Bob',
        'Middle Initial': 'L',
        'State': 'Columbus',
        'City': 'Ohio'
    }

    link1 = get_link_to_details(set1)
    logger.info(f'link: {link1}\n')

    link2 = get_link_to_details(set2)
    logger.info(f'link: {link2}\n')

    logger.info(get_link_to_details(set3))

    get_link_to_details(set_missing_input1)
    get_link_to_details(set_missing_input2)
