package com.sergio.crud.backend.services;

import com.sergio.crud.backend.dtos.GymRecordDto;
import com.sergio.crud.backend.entities.GymRecord;
import com.sergio.crud.backend.exceptions.AppException;
import com.sergio.crud.backend.mappers.GymRecordMapper;
import com.sergio.crud.backend.repositories.GymRecordsRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class RecordsService {

    private final GymRecordsRepository gymRecordsRepository;
    private final GymRecordMapper gymRecordMapper;

    public List<GymRecordDto> allRecords() {
        log.debug("Service: Fetching all gym records from DB");
        List<GymRecordDto> records = gymRecordMapper.toGymRecordDtos(gymRecordsRepository.findAll());
        log.debug("Service: Found {} records in DB", records.size());
        return records;
    }

    public GymRecordDto createGymRecords(GymRecordDto gymRecordDto) {
        log.info("Service: Saving new record - exercise={}, weight={}, diet={}",
                gymRecordDto.getExercise(), gymRecordDto.getWeight(), gymRecordDto.getDiet());
        GymRecord gymRecord = gymRecordMapper.toGymRecord(gymRecordDto);
        GymRecord savedGymRecord = gymRecordsRepository.save(gymRecord);
        log.info("Service: Record saved with id={}", savedGymRecord.getId());
        return gymRecordMapper.toGymRecordDto(savedGymRecord);
    }

    public GymRecordDto updateGymRecord(Long id, GymRecordDto recordDto) {
        log.info("Service: Updating record id={} - exercise={}, weight={}, diet={}",
                id, recordDto.getExercise(), recordDto.getWeight(), recordDto.getDiet());
        GymRecord record = gymRecordsRepository.findById(id)
                .orElseThrow(() -> {
                    log.warn("Service: Record not found for update, id={}", id);
                    return new AppException("Gym record not found", HttpStatus.NOT_FOUND);
                });
        gymRecordMapper.updateGymRecord(record, gymRecordMapper.toGymRecord(recordDto));
        GymRecord savedGymRecord = gymRecordsRepository.save(record);
        log.info("Service: Record id={} updated successfully", id);
        return gymRecordMapper.toGymRecordDto(savedGymRecord);
    }

    public GymRecordDto patchGymRecord(Long id, GymRecordDto recordDto) {
        log.info("Service: Patching record id={}", id);
        GymRecord record = gymRecordsRepository.findById(id)
                .orElseThrow(() -> {
                    log.warn("Service: Record not found for patch, id={}", id);
                    return new AppException("Gym record not found", HttpStatus.NOT_FOUND);
                });

        if (recordDto.getName() != null) {
            log.debug("Service: Patching name -> {}", recordDto.getName());
            record.setName(recordDto.getName());
        }

        if (recordDto.getExercise() != null) {
            log.debug("Service: Patching exercise -> {}", recordDto.getExercise());
            record.setExercise(recordDto.getExercise());
        }

        if (recordDto.getWeight() != null) {
            log.debug("Service: Patching weight -> {}", recordDto.getWeight());
            record.setWeight(recordDto.getWeight());
        }

        if (recordDto.getDiet() != null) {
            log.debug("Service: Patching diet -> {}", recordDto.getDiet());
            record.setDiet(recordDto.getDiet());
        }

        GymRecord savedRecord = gymRecordsRepository.save(record);
        log.info("Service: Record id={} patched successfully", id);
        return gymRecordMapper.toGymRecordDto(savedRecord);
    }

    public GymRecordDto deleteGymRecord(Long id) {
        log.info("Service: Deleting record id={}", id);
        GymRecord record = gymRecordsRepository.findById(id)
                .orElseThrow(() -> {
                    log.warn("Service: Record not found for delete, id={}", id);
                    return new AppException("Gym record not found", HttpStatus.NOT_FOUND);
                });
        GymRecordDto gymRecordDto = gymRecordMapper.toGymRecordDto(record);
        gymRecordsRepository.deleteById(id);
        log.info("Service: Record id={} (exercise={}) deleted successfully", id, record.getExercise());
        return gymRecordDto;
    }

    public GymRecordDto getGymRecord(Long id) {
        log.debug("Service: Fetching record id={}", id);
        GymRecord record = gymRecordsRepository.findById(id)
                .orElseThrow(() -> {
                    log.warn("Service: Record not found, id={}", id);
                    return new AppException("Gym record not found", HttpStatus.NOT_FOUND);
                });
        log.debug("Service: Found record id={}, exercise={}", id, record.getExercise());
        return gymRecordMapper.toGymRecordDto(record);
    }
}
