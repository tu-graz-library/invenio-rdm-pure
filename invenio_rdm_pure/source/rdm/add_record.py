import json
import time
import os.path
from datetime import date
from setup import (
    versioning_running,
    possible_record_restrictions,
    data_files_name,
    iso6393_file_name,
    push_dist_sec,
    accessright_pure_to_rdm,
)
from source.general_functions import (
    shorten_file_name,
    file_read_lines,
    check_if_file_exists,
    get_value,
)
from source.pure.general_functions import (
    get_pure_record_metadata_by_uuid,
    get_pure_file,
)
from source.pure.requests import get_pure_metadata
from source.rdm.general_functions import GeneralFunctions
from source.rdm.put_file import rdm_add_file
from source.rdm.emails import send_email
from source.rdm.versioning import Versioning
from source.rdm.run.groups import RdmGroups
from source.rdm.database import RdmDatabase
from source.rdm.requests import Requests
from source.reports import Reports


class RdmAddRecord:
    def __init__(self):
        self.rdm_requests = Requests()
        self.report = Reports()
        self.groups = RdmGroups()
        self.general_functions = GeneralFunctions()
        self.versioning = Versioning()
        self.rdm_db = RdmDatabase()

    def push_record_by_uuid(self, global_counters: dict, uuid: str):
        """ Gets from Pure the metadata of a given uuid """
        item = get_pure_record_metadata_by_uuid(uuid)
        if not item:
            return False
        return self.create_invenio_data(global_counters, item)

    def _set_initial_variables(func):
        def _wrapper(self, global_counters, item):
            self.global_counters = global_counters
            self.global_counters["total"] += 1

            self.uuid = item["uuid"]
            self.item = item
            # Stores the data that will be then converted to json
            self.data = {}
            # Stores the name of the record files
            # Necessary because we need first to create the record and then to put the files
            self.record_files = []

            # Stores all extra fields that are not in the standard RDM datamodel
            self.pure_extensions = {}

            # Decorated function
            func(self, global_counters, item)

        return _wrapper

    @_set_initial_variables
    def create_invenio_data(self, global_counters: dict, item: dict):
        """ Process the data received from Pure and submits it to RDM """

        # Versioning
        self._check_record_version()

        # Record owners
        self._check_record_owners()

        # Sets as '_created_by' the RDM userid of the
        userid = self.rdm_db.get_pure_admin_userid()
        if not userid:
            return False
        self.data["_created_by"] = userid

        # Access right
        access_right = self._accessright_conversion(
            get_value(item, ["openAccessPermissions", 0, "value"])
        )
        self.data["access_right"] = access_right

        # Metadata and files access
        access = get_value(item, ["confidential"])
        self.data["_access"] = {
            "metadata_restricted": access,
            "files_restricted": access,
        }

        # Language
        value = get_value(item, ["languages", 0, "value"])
        self.language = self._language_conversion(value)
        self.data["language"] = self.language

        # Title
        self._add_title()

        # Person Associations
        self._process_person_associations()

        # Description
        self._add_description()

        # Identifiers
        self._add_identifiers()

        # Resource type
        self._add_resource_type()

        # Access right and restrictions
        self._access_right_and_restrictions(item)

        # Process various general fields
        self._process_general_fields(item)

        # # Electronic Versions (files)
        self._process_electronic_versions()

        # Additional Files
        if "additionalFiles" in item:
            for i in item["additionalFiles"]:
                self.get_files_data(i)

        # Organisational Units
        self._process_organisational_units()

        # Checks if the restrictions applied to the record are valid
        self._applied_restrictions_check()

        # Add pure_extensions to the data to be submitted
        self.data["extensions"] = self.pure_extensions

        # Convert to json string
        self.data = json.dumps(self.data)

        # Post request to RDM
        self._post_metadata()

        # Updates the versioning data of all records with the same uuid
        self._update_all_uuid_versions()

    def _access_right_and_restrictions(self, item):
        # Access right
        permission = get_value(item, ["openAccessPermissions", 0, "value"])
        self.data["access_right"] = self._accessright_conversion(permission)

        # Restrictions
        if permission != "Open":
            self.data["applied_restrictions"] = [
                "owners",
                "groups",
                "ip_single",
                "ip_range",
            ]

    def _add_resource_type(self):
        # To REVIEW
        # Pure: Conference contribution, Article, Lecture or Presentation, Poster, Chapter, Other report, Book, Doctoral Thesis, Master's Thesis, Diploma Thesis, Commissioned report, ...
        # RDM:  publication, poster, presentation, dataset, image, video, software, lesson, other

        # - RDM -         - PURE -
        # publication       Conference contribution, Article, Chapter, (...) Thesis
        # poster            Poster
        # presentation      Lecture or Presentation,
        # dataset
        # image
        # video
        # software
        # lesson
        # other             Other report
        self.data["resource_type"] = {
            "type": "publication",
            "subtype": "publication-other",
        }

    def _add_title(self):
        title = get_value(self.item, ["title"])
        self.data["titles"] = [
            {"lang": self.language, "title": title, "type": "MainTitle"}
        ]

    def _add_description(self):
        abstract = get_value(self.item, ["abstracts", 0, "value"])
        if not abstract:
            abstract = "No description available for this record."
        self.data["descriptions"] = [
            {"description": abstract, "lang": self.language, "type": "Abstract"}
        ]

    def _add_identifiers(self):
        self.data["version"] = "v0.0.2"

        self.data["identifiers"] = {  # TO REVIEW
            "DOI": "10.5281/rdm.9999992",  # Digital Object Identifiers
        }

    def _versioning_required(func):
        def _wrapper(self):
            if not versioning_running:
                return
            func(self)

        return _wrapper

    @_versioning_required
    def _check_record_version(self):
        """ Checks if there are in RDM other versions of the same uuid """
        # Get metadata version
        response = self.versioning.get_uuid_version(self.uuid)
        if response:
            self.data["metadataVersion"] = response[0]
            self.data["metadataOtherVersions"] = response[1]

    @_versioning_required
    def _update_all_uuid_versions(self):
        """ Updates the versioning data of all records with the same uuid """
        self.versioning.update_all_uuid_versions(self.uuid)

    def _check_record_owners(self):
        """ Removes duplicate owners """
        if "_owners" in self.item:
            self.data["_owners"] = list(set(self.item["_owners"]))
        else:
            self.data["_owners"] = list(set([1]))

    def _process_general_fields(self, item: dict):
        # Parameters:
        # 1- Pure records data
        # 2- RDM field
        # 3- Path to field value in Pure json
        self._add_extension(item, "tug:uuid", ["uuid"])
        self._add_extension(item, "tug:publisherUuid", ["publisher", "uuid"])
        self._add_extension(item, "tug:pages", ["info", "pages"])
        self._add_extension(item, "tug:volume", ["info", "volume"])
        path = ["publicationStatuses", 0, "publicationDate", "year"]
        self._add_extension(item, "tug:publication_date", path)
        self._add_extension(
            item, "tug:journalTitle", ["info", "journalAssociation", "title", "value"]
        )
        self._add_extension(item, "tug:journalNumber", ["info", "journalNumber"])
        self._add_extension(item, "tug:pure_link", ["info", "portalUrl"])
        self._add_extension(item, "tug:pure_type", ["types", 0, "value"])
        self._add_extension(item, "tug:pure_category", ["categories", 0, "value"])
        self._add_extension(item, "tug:peerReview", ["peerReview"])
        path = ["publicationStatuses", 0, "publicationStatuses", 0, "value"]
        self._add_extension(item, "tug:publicationStatus", path)
        self._add_extension(item, "tug:workflow", ["workflows", 0, "value"])
        self._add_extension(
            item, "tug:publisherName", ["publisher", "names", 0, "value"]
        )
        self._add_extension(
            item, "tug:publisherType", ["publisher", "types", 0, "value"]
        )
        path = ["managingOrganisationalUnit", "names", 0, "value"]
        self._add_extension(item, "tug:managingOrganisationalUnit_name", path)
        path = ["managingOrganisationalUnit", "uuid"]
        self._add_extension(item, "tug:managingOrganisationalUnit_uuid", path)
        path = ["managingOrganisationalUnit", "externalId"]
        self._add_extension(item, "tug:managingOrganisationalUnit_externalId", path)

    def _add_extension(self, item: dict, rdm_field: str, path: list):
        """ Adds the field to Pure extension """
        value = get_value(item, path)
        if value:
            self.pure_extensions[rdm_field] = value

    def _process_electronic_versions(self):
        """ Data relative to files """
        self.rdm_file_review = []

        if "electronicVersions" in self.item or "additionalFiles" in self.item:
            # Checks if the file has been already uploaded to RDM and if it has been internally reviewed
            self._get_rdm_file_review()

        if "electronicVersions" in self.item:
            for i in self.item["electronicVersions"]:
                self.get_files_data(i)

    def _process_person_associations(self):
        """ Process data ralative to the record creators """
        if "personAssociations" not in self.item:
            return

        self.data["creators"] = []

        file_data = file_read_lines("user_ids_match")

        for item in self.item["personAssociations"]:

            self.sub_data = {}
            # Name
            self._get_contributor_name(item)

            # Organizational, Personal
            self.sub_data["type"] = "Personal"  # Organizational / Personal

            # - Identifiers -
            self.sub_data["identifiers"] = {}
            self._add_field_sub(item, "identifiers", "uuid", ["person", "uuid"])
            self._add_field_sub(
                item, "identifiers", "externalId", ["person", "externalId"]
            )
            self._add_field_sub(item, "identifiers", "uuid", ["externalPerson", "uuid"])
            # Orcid
            self._process_contributor_orcid()

            # Affiliations
            self.sub_data["affiliations"] = []
            if "organisationalUnits" in item:
                for i in item["organisationalUnits"]:
                    name = get_value(i, ["names", 0, "value"])
                    externalId = get_value(i, ["externalId"])
                    uuid = get_value(i, ["uuid"])
                    if name and externalId:
                        self.sub_data["affiliations"].append(
                            {
                                "name": name,
                                "identifiers": {
                                    "externalId": externalId,
                                    "uuid": uuid,
                                },
                            }
                        )

            # Checks if the record owner is available in user_ids_match.txt
            person_external_id = get_value(item, ["person", "externalId"])
            owner = self.general_functions.get_userid_from_list_by_externalid(
                person_external_id, file_data
            )
            if owner and int(owner) not in self.data["_owners"]:
                self.data["_owners"].append(int(owner))

            # Append person to creators
            self.data["creators"].append(self.sub_data)

    def _add_field_sub(
        self, item: list, rdm_field_1: str, rdm_field_2: str, path: list
    ):
        """ Adds the field to sub_data """
        value = get_value(item, path)
        if value:
            self.sub_data[rdm_field_1][rdm_field_2] = value

    def _get_contributor_name(self, item: object):
        first_name = get_value(item, ["name", "firstName"])
        last_name = get_value(item, ["name", "lastName"])

        if not first_name:
            first_name = "(first name not specified)"
        if not last_name:
            last_name = "(last name not specified)"

        self.sub_data["name"] = f"{first_name} {last_name}"

    def _process_contributor_orcid(self):
        if "uuid" in self.sub_data:
            person_uuid = self.sub_data["uuid"]
            person_name = self.sub_data["name"]

            # External persons are not present in 'persons' Pure API endpoint
            if (
                "type_p" in self.sub_data
                and self.sub_data["type_p"] == "External person"
            ):
                report = f"\tPure get orcid @@ External person @ {person_uuid} @ {person_name}"
                self.report.add(report)
            else:
                orcid = self._get_orcid(person_uuid, person_name)
                if orcid:
                    self.sub_data["identifiers"]["orcid"] = orcid

    def _process_organisational_units(self):
        """ Process the metadata relative to the organisational units """
        if "organisationalUnits" in self.item:
            self.data["group_restrictions"] = []

            for i in self.item["organisationalUnits"]:

                organisational_unit_name = get_value(i, ["names", 0, "value"])
                organisational_unit_uuid = get_value(i, ["uuid"])
                organisational_unit_externalId = get_value(i, ["externalId"])

                if not organisational_unit_externalId:
                    continue

                # Adding organisational unit as group owner
                self.data["group_restrictions"].append(organisational_unit_externalId)

                # Create group
                self.groups.rdm_create_group(
                    organisational_unit_externalId, organisational_unit_name
                )

    def _applied_restrictions_check(self):
        """ Checks if the restrictions applied to the record are valid.
            e.g. ['groups', 'owners', 'ip_range', 'ip_single'] """
        if not "applied_restrictions" in self.data:
            return False

        for i in self.data["applied_restrictions"]:
            if i not in possible_record_restrictions:
                report = (
                    f"Warning: the value '{i}' is not among the accepted restrictions\n"
                )
                self.report.add(report)
        return True

    def _post_metadata(self):
        """ Submits the created json to RDM """
        uuid = self.item["uuid"]
        success_check = {"metadata": False, "file": False}

        # POST REQUEST metadata
        response = self.rdm_requests.post_metadata(self.data)

        # Process response
        if not self._process_post_response(response, uuid):
            return False

        success_check["metadata"] = True

        # After pushing a record's metadata to RDM it takes about one second to be able to get its recid
        time.sleep(1)

        # Gets recid from RDM
        recid = self.general_functions.get_recid(uuid, self.global_counters)
        if not recid:
            return False

        # add record to all_rdm_records.txt
        open(data_files_name["all_rdm_records"], "a").write(f"{uuid} {recid}\n")

        # Submit record FILES
        for file_name in self.record_files:

            # Submit request
            response = rdm_add_file(file_name, recid)
            # Process response
            successful = self._process_file_response(response, success_check)

            # if successful:
            # # Sends email to remove record from Pure
            # send_email(uuid, file_name)

        if not self.record_files:
            success_check["file"] = True

        # Checks if both metadata and files were correctly transmitted
        self._metadata_and_file_submission_check(success_check)

    def _process_post_response(self, response: object, uuid: str):
        # Count http responses
        self._http_response_counter(response.status_code)

        self.report.add(
            f"\tRDM post metadata @ {response} @ Uuid:                 {uuid}"
        )

        if response.status_code >= 300:
            self.global_counters["metadata"]["error"] += 1
            return False

        self.global_counters["metadata"]["success"] += 1
        return True

    def _process_file_response(self, response: object, success_check: object):
        if response:
            self.global_counters["file"]["success"] += 1
            success_check["file"] = True

        else:
            self.global_counters["file"]["error"] += 1

    def _remove_uuid_from_list(self, uuid: str, file_name: str):
        """ If the given uuid is in the given file then the line will be removed """
        check_if_file_exists(file_name)

        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != uuid:
                    f.write(line)

    def _add_field(self, item: list, rdm_field: str, path: list):
        """ Adds the field to the data json """
        value = get_value(item, path)
        if value:
            self.data[rdm_field] = value
        return

    def _accessright_conversion(self, pure_value: str):
        """ Converts the Pure access right to the corresponding RDM value """
        if pure_value in accessright_pure_to_rdm:
            return accessright_pure_to_rdm[pure_value]

        self.report.add(
            "\n--- new access_right ---> not in accessright_pure_to_rdmk array\n\n"
        )
        return False

    def _language_conversion(self, pure_language: str):
        """ Converts from pure full language name to iso6393 (3 characters) """
        if pure_language == "Undefined/Unknown":
            return False

        # Read iso6393 json file
        resp_json = json.load(open(iso6393_file_name, "r"))

        for i in resp_json:
            if i["name"] == pure_language:
                return i["iso6393"]

        # in case there is no match (e.g. spelling mistake in Pure) ignore field
        return False

    def _get_rdm_file_review(self):
        """ 
        When a record is updated in Pure, there will be a check 
        if the new file from Pure is the same as the old file in RDM.
        To do so it makes a comparison on the file size.
        If the size is not the same, then it will be uploaded to RDM 
        and a new internal review will be required. 
        """

        # Get from RDM file size and internalReview
        params = {"sort": "mostrecent", "size": "100", "page": "1", "q": self.uuid}
        response = self.rdm_requests.get_metadata(params)

        if response.status_code >= 300:
            self.report.add(f"\nget_rdm_file_size @ {self.uuid} @ {response}")
            return False

        # Load response
        resp_json = json.loads(response.content)

        total_recids = resp_json["hits"]["total"]
        if total_recids == 0:
            return False

        record = resp_json["hits"]["hits"][0][
            "metadata"
        ]  # [0] because they are ordered, therefore it is the most recent

        if "versionFiles" in record:
            for file in record["versionFiles"]:
                if "size" in file and "internalReview" in file and "name" in file:
                    file_size = file["size"]
                    file_review = file["internalReview"]
                    file_name = file["name"]
                    self.rdm_file_review.append(
                        {"size": file_size, "review": file_review, "name": file_name}
                    )

    def get_files_data(self, item: dict):
        """ Gets metadata information from electronicVersions and additionalFiles files.
            It also downloads the relative files. The Metadata without file will be ignored """
        if "file" not in item:
            return False
        elif "fileURL" not in item["file"] or "fileName" not in item["file"]:
            return False

        internal_review = False  # Default value

        pure_file_size = get_value(item, ["file", "size"])
        file_name = get_value(item, ["file", "fileName"])
        file_url = get_value(item, ["file", "fileURL"])

        self.pure_rdm_file_match = []

        # Checks if pure_file_size and file_name are the same as any of the files in RDM with the same uuid
        for rdm_file in self.rdm_file_review:

            rdm_file_size = str(rdm_file["size"])
            rdm_review = rdm_file["review"]

            if pure_file_size == rdm_file_size and file_name == rdm_file["name"]:
                self.pure_rdm_file_match.append(True)  # Do the old and new file match?
                self.pure_rdm_file_match.append(
                    rdm_review
                )  # Was the old file reviewed?
                internal_review = rdm_review  # The new uploaded file will have the same review value as in RDM
                break

        self.sub_data = {}
        self.pure_extensions["tug:file_internalReview"] = internal_review

        self._add_extension(item, "tug:file_name", ["file", "fileName"])
        self._add_extension(item, "tug:file_createdBy", ["creator"])
        self._add_extension(item, "tug:file_createdDate", ["created"])
        self._add_extension(item, "tug:file_versionType", ["versionTypes", 0, "value"])
        self._add_extension(item, "tug:file_licenseType", ["licenseTypes", 0, "value"])
        self._add_extension(item, "tug:file_digest", ["file", "digest"])
        self._add_extension(
            item, "tug:file_digestAlgorithm", ["file", "digestAlgorithm"]
        )

        # Access type
        value = get_value(item, ["accessTypes", 0, "value"])
        self.sub_data["accessType"] = self._accessright_conversion(value)

        # Download file from Pure
        response = get_pure_file(self, file_url, file_name)
        # Checks if the file is already in RDM, and if it has already been reviewed
        self._process_file_download_response(response, file_name)

    def _add_subdata(self, item: list, rdm_field: str, path: list):
        """ Adds the field to sub_data """
        value = get_value(item, path)
        if value:
            self.sub_data[rdm_field] = value

    def _process_file_download_response(self, response, file_name):
        """ Checks if the file is already in RDM, and if it has already been reviewed """
        # If the file is not in RDM
        if len(self.pure_rdm_file_match) == 0:
            match_review = "File not in RDM    "

        # If the file in pure is different from the one in RDM
        elif self.pure_rdm_file_match[0] == False:
            match_review = "Match: F, Review: -"

        # If the file is the same, checks if the one in RDM has been reviewed by internal stuff
        else:
            match_review = "Match: T, Review: F"
            if self.pure_rdm_file_match[1]:
                match_review = "Match: T, Review: T"

        file_name_report = shorten_file_name(file_name)

        report = f"\tPure get file @ {response} @ {match_review} @ {file_name_report}"
        self.report.add(report)

        self.record_files.append(file_name)

    def _get_orcid(self, person_uuid: str, name: str):
        """ Gets from pure a person orcid """
        # Pure request
        response = get_pure_metadata("persons", person_uuid, {}, False)

        message = f"\tPure get orcid @ {response} @"

        # Error
        if response.status_code >= 300:
            self.report.add(f"{message} Error: {response.content}")
            return False

        # Load json
        resp_json = json.loads(response.content)

        # Read orcid
        if "orcid" in resp_json:
            orcid = resp_json["orcid"]
            self.report.add(f"{message} {orcid} @ {person_uuid} @ {name}")
            return orcid

        # Not found
        self.report.add(f"{message} Orcid not found @ {person_uuid} @ {name}")
        return False

    def _metadata_and_file_submission_check(self, success_check: dict):
        """ Checks if both metadata and files were correctly transmitted """
        if success_check["metadata"] == True and success_check["file"] == True:
            # Remove uuid from to_transmit.txt
            self._remove_uuid_from_list(
                self.uuid, data_files_name["transfer_uuid_list"]
            )
        else:
            # Add uuid to to_transmit.txt to be re-transmitted
            open(data_files_name["transfer_uuid_list"], "a").write(f"{self.uuid}\n")
            return False
        return True

    def _http_response_counter(self, status_code: int):
        """ According to the given http status code creates 
            a new object element or increaes an existing one  """
        if status_code not in self.global_counters["http_responses"]:
            self.global_counters["http_responses"][status_code] = 0
        self.global_counters["http_responses"][status_code] += 1
